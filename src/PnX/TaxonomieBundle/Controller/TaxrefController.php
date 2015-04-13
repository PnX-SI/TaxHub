<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\Taxref;
use PnX\TaxonomieBundle\Entity\BibTaxrefHabitats;
use PnX\TaxonomieBundle\Entity\BibTaxrefRangs;
use PnX\TaxonomieBundle\Entity\TaxrefProtectionEspeces;
use PnX\TaxonomieBundle\Entity\TaxrefProtectionArticles;
use JSM\Serializer\SerializerBuilder;

use PnX\TaxonomieBundle\Generic\DoctrineFunctions;

/**
 * Taxref controller.
 *
 */
class TaxrefController extends Controller
{

    /**
     * Récupération d'une liste des enregistrements de l'entité taxref qui correspondent aux critères demandés
     *
     */
    public function getTaxrefListAction() {
        $em = $this->getDoctrine()->getManager();
        
        //Paramètres de paginations
        $limit = $this->getRequest()->get('limit', 50);
        $page = $this->getRequest()->get('page', 0);
        
        //Paramètres des filtres des données
        $qparameters=[];
        $where=[];
        $getParamsKeys = $this->getRequest()->query->keys();
        $fieldsName = (new DoctrineFunctions($em))->getEntityFieldList('Taxref');
        foreach($getParamsKeys as $index => $key) {
            if($this->getRequest()->get($key) != null && $this->getRequest()->get($key) !=''){
                if ($key==='nom_valide') {
                  if ($this->getRequest()->get($key) === true ) {
                    $where[]='taxref.cdNom = taxref.cdRef ';
                  }
                }
                elseif ($key==='ilike') {
                    $where[]='lower(taxref.lbNom) like lower(:lb_nom)';
                    $qparameters['lb_nom']=$this->getRequest()->get($key).'%';
                }
                elseif(in_array ($key ,$fieldsName)) {
                    $where[]='taxref.'.$key.'= :'.$key;
                    $qparameters[$key]=$this->getRequest()->get($key);
                }
            }
        }
        
        //Récupération des entités correspondant aux critères
        $entities = $em->getRepository('PnXTaxonomieBundle:Taxref')->findAllPaginated($page, $limit, $where, $qparameters);
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }

    /**
     * Finds and displays a Taxref entity.
     *
     */
    public function getTaxRefDetailAction($id){
      try {
        $em = $this->getDoctrine()->getManager();
        $serializer = $this->get('jms_serializer');

        $taxref = $em->getRepository('PnXTaxonomieBundle:Taxref')->find($id);
        
        $jsonObject =  $serializer->serialize($taxref, 'json');
        $entity =  json_decode($jsonObject);
        
        if (!$taxref) {
            throw $this->createNotFoundException('Unable to find Taxref entity.');
        }
        if ($taxref->getIdHabitat()) {
          $habitat = $em->getRepository('PnXTaxonomieBundle:BibTaxrefHabitats')->find($taxref->getIdHabitat());
          $entity->nom_habitat = $habitat->getNomHabitat();
        }
        if ($taxref->getIdRang()) {
          $rang = $em->getRepository('PnXTaxonomieBundle:BibTaxrefRangs')->find($taxref->getIdRang());
          $entity->nom_rang = $rang->getNomRang();
        }
        if ($taxref->getIdStatut()) {
          $rang = $em->getRepository('PnXTaxonomieBundle:BibTaxrefStatuts')->find($taxref->getIdStatut());
          $entity->nom_statut = $rang->getNomStatut();
        }
        
       $synonymes = $em->getRepository('PnXTaxonomieBundle:Taxref')->findSynonymsList($taxref->getCdRef());
       $entity->synonymes = $synonymes;
        
        $prStatutQry = $em->getConnection()->prepare("SELECT DISTINCT pr_a.* 
          FROM taxonomie.taxref_protection_articles pr_a
          JOIN (SELECT * FROM taxonomie.taxref_protection_especes pr_sp WHERE taxonomie.find_cdref(pr_sp.cd_nom) = ".$taxref->getCdRef().") pr_sp
          ON pr_a.cd_protection = pr_sp.cd_protection
          WHERE NOT concerne_mon_territoire IS NULL ");
        $prStatutQry->execute();
        $prStatutList = $prStatutQry->fetchAll();
        $entity->statuts_protection = $prStatutList;
  
        return new JsonResponse($entity, 200, array('content-type' => 'application/json'));
      } catch (\Exception $exception) {
          return new JsonResponse([
              'success' => false,
              'code'    => $exception->getCode(),
              'message' => $exception->getMessage(),
          ]);
      }
      
    }
    
    public function getDistinctFieldAction($field) {
        
        $getParamsKeys = $this->getRequest()->query->keys();
        $where=[];
        $qparameters=[];
        
        $em = $this->getDoctrine()->getManager();
        $fieldsName = (new DoctrineFunctions($em))->getEntityFieldList('Taxref');
        
        foreach($getParamsKeys as $index => $key) {
            if($this->getRequest()->get($key) != null && $this->getRequest()->get($key) !=''){
                if ($key==='ilike') {
                    $where[]='lower(taxref.'.$field.') like lower(:nom_complet)';
                    $qparameters['nom_complet']=$this->getRequest()->get($key).'%';
                }
                elseif(in_array ($key ,$fieldsName)) {
                    $where[]='taxref.'.$key.'= :'.$key;
                    $qparameters[$key]=$this->getRequest()->get($key);
                }
            }
        }

        $em = $this->getDoctrine()->getManager();
        $results= $em->getRepository('PnXTaxonomieBundle:Taxref')->findDistinctValueForOneFieldWithParams($field, $where, $qparameters);

        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }
    
    /**
     * Récupération des niveaux hiérarchique du taxref
     *
     */
    public function getTaxrefHierarchieAction($rang) {
        $em = $this->getDoctrine()->getManager();
        
        //Paramètres de paginations
        $limit = $this->getRequest()->get('limit', 10);
        
        //Paramètres des filtres des données
        $qparameters=[];
        $where=[];
        $getParamsKeys = $this->getRequest()->query->keys();
        $fieldsName = (new DoctrineFunctions($em))->getEntityFieldList('VmTaxrefHierarchie');
        foreach($getParamsKeys as $index => $key) {
            
            if($this->getRequest()->get($key) != null && $this->getRequest()->get($key) !=''){
                if ($key==='ilike') {
                    $where[]='lower(VmTaxrefHierarchie.lbNom) like lower(:lb_nom)';
                    $qparameters['lb_nom']=$this->getRequest()->get($key).'%';
                }
                elseif(in_array ($key ,$fieldsName)) {
                    $where[]='VmTaxrefHierarchie.'.$key.'= :'.$key;
                    $qparameters[$key]=$this->getRequest()->get($key);
                }
            }
            if (isset($rang)) {
                $where[]='VmTaxrefHierarchie.idRang =:id_rang';
                $qparameters['id_rang']=$rang;
            }
        }
        
        //Récupération des entités correspondant aux critères
        $entities = $em->getRepository('PnXTaxonomieBundle:VmTaxrefHierarchie')->findLimitedTaxrefHierarchie($limit, $where, $qparameters);
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }
}
