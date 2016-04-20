<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\BibTaxons;

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
                'idTaxon' => $value->getIdTaxon(),
                'nomLatin' => $value->getNomLatin(),
                'auteur' => $value->getAuteur(),
                'nomFrancais' => $value->getNomFrancais()
            );
            $taxonTaxo = [];
            if ($value->getCdNom() !== null) {
               $taxonTaxo =  array(
                'cdNom' => $value->getCdNom()->getCdNom(),
                'regne' => $value->getCdNom()->getRegne(),
                'phylum' => $value->getCdNom()->getPhylum(),
                'classe' => $value->getCdNom()->getClasse(),
                'ordre' => $value->getCdNom()->getOrdre(),
                'famille' => $value->getCdNom()->getFamille(),
                'nomValide' => $value->getCdNom()->getNomValide()
                );
            }
            $taxonList[]=array_merge($taxon, $taxonTaxo);
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
        $entity = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($entity, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }
    
    
    /**
     * Edits an existing BibTaxons entity.
     *
     */
    public function createUpdateAction(Request $request, $id){
        $em = $this->getDoctrine()->getManager();
        $post = $this->getRequest()->getContent();
        $post = json_decode($post);
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
        if (isset($post->nomFrancais))  $entity->setNomFrancais($post->nomFrancais);
        if (isset($post->nomLatin))  $entity->setNomLatin($post->nomLatin);
        if (isset($post->auteur))  $entity->setAuteur($post->auteur);
        if (isset($post->cdNom)) {
            //@TODO différence entre getReference et getRepository()->find()
            $taxon = $em->getReference('\PnX\TaxonomieBundle\Entity\Taxref', $post->cdNom);
            if ($taxon) {
                $entity->setcdNom($taxon);
            }
        }
        
        $validator = $this->get('validator');
        
        $errorList= $validator->validate($entity);
       
       if (count($errorList) > 0) {
          foreach( $errorList as $key => $value) {
              return new JsonResponse([
                    'success' => false,
                    'code'    =>-10,
                    'message' => $value->getMessage(),
                ]);
            }
        } else {
            try {
                $em->persist($entity);
                $em->flush();
                return new JsonResponse([
                    'success' => true,
                    'message' => 'Entité MAJ',
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
