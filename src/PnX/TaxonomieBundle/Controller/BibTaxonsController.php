<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\BibTaxons;
use PnX\TaxonomieBundle\Entity\CorTaxonAttribut;

use JSM\Serializer\SerializerBuilder;
/**
 * BibTaxons controller.
 *
 */
class BibTaxonsController extends Controller
{

    /**
     * Lists all BibTaxons entities.
     *
     */
    public function getAction() {
        $em = $this->getDoctrine()->getManager();
        
        $entities = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->findAll();
        
        $taxonList=[];
        foreach ($entities as $key => $value) {
            $taxon =  array(
                'id_taxon' => $value->getIdTaxon(),
                'nom_latin' => $value->getNomLatin(),
                'auteur' => $value->getAuteur(),
                'nom_francais' => $value->getNomFrancais(),
                'cd_nom' => $value->getCdNom()
            );
            // $taxonTaxo = [];
            // if ($value->getTaxref() !== null) {
               // $taxonTaxo =  array(
                // 'cd_nom' => $value->getTaxref()->getCdNom(),
                // 'regne' => $value->getTaxref()->getRegne(),
                // 'phylum' => $value->getTaxref()->getPhylum(),
                // 'classe' => $value->getTaxref()->getClasse(),
                // 'ordre' => $value->getTaxref()->getOrdre(),
                // 'famille' => $value->getTaxref()->getFamille(),
                // 'nom_valide' => $value->getTaxref()->getNomValide()
                // );
            // }
            // $taxonList[]=array_merge($taxon, $taxonTaxo);
            array_push($taxonList,$taxon);
        }
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($taxonList, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }
    
    public function getTaxonomieAction() {
        try {
            $em = $this->getDoctrine()->getManager();
            $results =  $em->getRepository('PnXTaxonomieBundle:BibTaxons')->getTaxonomieHierarchie();
            $serializer = $this->get('jms_serializer');
            $jsonContent = $serializer->serialize($results, 'json');
            return new Response($jsonContent, 200, array('content-type' => 'application/json'));
        } 
        catch (\Exception $exception) {
            return new JsonResponse([
                'success' => false,
                'code'    => $exception->getCode(),
                'message' => $exception->getMessage(),
            ]);
        }
    }
    
     /**
     * Finds and displays a BibTaxons entity.
     *
     */
    public function getOneAction($id){
        $em = $this->getDoctrine()->getManager();
        $serializer = $this->get('jms_serializer');
        $value = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);
        $taxon =  array(
            'id_taxon' => $value->getIdTaxon(),
            'nom_latin' => $value->getNomLatin(),
            'auteur' => $value->getAuteur(),
            'nom_francais' => $value->getNomFrancais(),
            'cd_nom' => $value->getCdNom()
        );

        $attributs = $em->getRepository('PnXTaxonomieBundle:BibAttributs')->findAttributsByOneTaxon($id);
        $taxon['attributs'] = $attributs;
        $jsonContent =  $serializer->serialize($taxon, 'json');

        return new JsonResponse($taxon, 200, array('content-type' => 'application/json'));
    }
    
    
    /**
     * Edits an existing BibTaxons entity.
     *
     */
    public function createUpdateAction(Request $request, $id){
        $em = $this->getDoctrine()->getManager();
        $post = $this->getRequest()->getContent();
        $post = json_decode($post);
        
        $status = false;
        $code = 200;
        $message = "Attribut ajouté";
        $nbAttributs = 0;
        //UPDATE
        if ($id != null) {
            $entity = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);
            if (!$entity) {
                throw $this->createNotFoundException('Unable to find BibTaxons entity.');
            }
        }
        else{ //INSERT
            $entity = new BibTaxons();
        }
        if (isset($post->nom_francais))  $entity->setNomFrancais($post->nom_francais);
        if (isset($post->nom_latin))  $entity->setNomLatin($post->nom_latin);
        if (isset($post->auteur))  $entity->setAuteur($post->auteur);
        if (isset($post->cd_nom))  $entity->setCdNom($post->cd_nom);
        if (isset($post->cd_nom)) {
            //@TODO différence entre getReference et getRepository()->find()
            $taxon = $em->getReference('\PnX\TaxonomieBundle\Entity\Taxref', $post->cd_nom);
            if ($taxon) {
                $entity->setTaxref($taxon);
            }
        }
        // print_r($entity);
        
        $validator = $this->get('validator');
        
        $errorList= $validator->validate($entity);
       
       if (count($errorList) > 0) {
          foreach( $errorList as $key => $value) {
                $status = false;
                $code = -10;
                $message = $value->getMessage();
                $nbAttributs = 0;
            }
        } else {
            try {
                $em->persist($entity);
                $em->flush();
                $status = true;
                $code = 200;
                $message = "Taxon mis à jour";
                
                $id_taxon = $entity->getIdTaxon();
                $attributs = $post->attributs_values;
                // $em->getRepository('PnXTaxonomieBundle:CorTaxonAttribut')->createTaxonAttributs($id_taxon,$attributs);
                
                //enregistrement des attribut du taxon
                $entities= $em->getRepository('PnXTaxonomieBundle:CorTaxonAttribut')->findByIdTaxon($id_taxon);
                //on test si le taxon a déjà des attributs ou pas, si oui on delete tous les enregistrements de ce taxon
                if($entities){
                    foreach($entities AS $entity){
                        $em->remove($entity);
                        $em->flush();
                    }
                }
                foreach($attributs as $key => $value){
                    $attribut = new CorTaxonAttribut();
                    $attribut->setIdTaxon($id_taxon);
                    $attribut->setIdAttribut($key);
                    $attribut->setValeurAttribut($value);
                    try {
                        $em->persist($attribut);
                        $em->flush();
                        $status = true;
                        $nbAttributs++;
                        $message .= "";
                    } 
                    catch (\Exception $exception) {
                        $status = false;
                        $code = $exception->getCode();
                        $message = $exception->getMessage();
                    }
                }
                $message .= $nbAttributs. " attribut(s) ajouté(s)";

            } catch (\Exception $exception) {
                $status = false;
                $code = $exception->getCode();
                $message = $exception->getMessage();
            }
            
        }
        return new JsonResponse([
            'success' => $status,
            'code'    => $code,
            'message' => $message,
            'nbattribut' => $nbAttributs,
        ]);
    }
    
    /**
     * Deletes a BibTaxons entity.
     *
     */
    public function deleteAction(Request $request, $id){
        $em = $this->getDoctrine()->getManager();
        $entity = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);

        if (!$entity) {
            return new JsonResponse([
                'success' => false,
                'code'    => -10,
                'message' => "Ce taxon n'existe pas",
            ]);
        }
        try {
            $nomtaxon = $entity->getNomLatin();
            $em->remove($entity);
            $em->flush();
            return new JsonResponse([
                'success' => true,
                'message' => $nomtaxon.' a été supprimé de la table bib_taxons',
                'data'    => []
                
            ]);
        } catch (\Exception $exception) {

            return new JsonResponse([
                'success' => false,
                'code'    => $exception->getCode(),
                'message' => $exception->getMessage(),
            ]);
        }
    }

}
