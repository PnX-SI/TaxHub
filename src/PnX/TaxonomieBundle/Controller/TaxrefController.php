<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\Taxref;
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
    public function indexAction() {
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
                  if ($this->getRequest()->get($key) == true ) {
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
    public function showAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:Taxref')->find($id);

        if (!$entity) {
            throw $this->createNotFoundException('Unable to find Taxref entity.');
        }
        
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($entity, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
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
