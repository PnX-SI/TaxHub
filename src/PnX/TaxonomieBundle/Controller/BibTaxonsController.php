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
     * Lists all BibTaxons entities. y
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
                'nomFrancais' => $value->getNomFrancais(),
                'filtre1' => $value->getFiltre1(),
                'filtre2' => $value->getFiltre2(),
                'filtre3' => $value->getFiltre3(),
                'filtre4' => $value->getFiltre4(),
                'filtre5' => $value->getFiltre5(),
                'filtre6' => $value->getFiltre6(),
                'filtre7' => $value->getFiltre7(),
                'filtre8' => $value->getFiltre8(),
                'filtre9' => $value->getFiltre9(),
                'filtre10'  => $value->getFiltre10()
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
        return new Response($jsonContent); 
    }
    
    public function getTaxonomieAction() {
        $em = $this->getDoctrine()->getManager();
         
       /* $taxonQry = $em->createQueryBuilder('qb1')
            ->add('select', 't.regne, t.phylum, t.classe, t.ordre, t.famille')
            ->add('from', 'PnXTaxonomieBundle:BibTaxons a')
            ->join('a.cdNom', 't')
            ->distinct()
            ->getQuery();

        $results= $taxonQry->getResult();
        */
        $connection = $em->getConnection();
        $statement = $connection->prepare("WITH tax as (
                SELECT t.*
                FROM taxonomie.taxref t
                JOIN taxonomie.bib_taxons b
                ON t.cd_nom = b.cd_nom
            ) 
            SELECT DISTINCT cd_nom, cd_taxsup, lb_nom, id_rang AS id_rang 
            FROM taxonomie.taxref WHERE id_rang IN ('KD','PH','CL','OR','FM')
            AND lb_nom IN (
                SELECT DISTINCT phylum FROM tax
                UNION
                SELECT DISTINCT regne FROM tax
                UNION
                SELECT DISTINCT classe FROM tax
                UNION
                SELECT DISTINCT ordre FROM tax
                UNION
                SELECT DISTINCT famille FROM tax
            )");
        $statement->execute();
        $results = $statement->fetchAll();
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response(  $jsonContent); // or return it in a Response
    }
    
     /**
     * Finds and displays a BibTaxons entity.
     *
     */
    public function getOneAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);
    
        
        $serializer = $this->get('jms_serializer');
        //$jsonContent = $serializer->serialize($p, 'json');
        $jsonContent = $serializer->serialize($entity, 'json');
        return new Response(  $jsonContent); // or return it in a Response
    }
    
    
    /**
     * Edits an existing BibTaxons entity.
     *
     */
    public function createUpdateAction(Request $request, $id)
    {
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
        if (isset($post->filtre1))  $entity->setFiltre1($post->filtre1);
        if (isset($post->filtre2))  $entity->setFiltre2($post->filtre2);
        if (isset($post->filtre3))  $entity->setFiltre3($post->filtre3);
        if (isset($post->filtre4))  $entity->setFiltre4($post->filtre4);
        if (isset($post->filtre5))  $entity->setFiltre5($post->filtre5);
        if (isset($post->filtre6))  $entity->setFiltre6($post->filtre6);
        if (isset($post->filtre7))  $entity->setFiltre7($post->filtre7);
        if (isset($post->filtre8))  $entity->setFiltre8($post->filtre8);
        if (isset($post->filtre9))  $entity->setFiltre9($post->filtre9);
        if (isset($post->filtre10))  $entity->setFiltre10($post->filtre10);
        
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
        return new Response('syper'); // or return it in a Response
    }
    /**
     * Deletes a BibTaxons entity.
     *
     */
    public function deleteAction(Request $request, $id)
    {
        $em = $this->getDoctrine()->getManager();
        $entity = $em->getRepository('PnXTaxonomieBundle:BibTaxons')->find($id);

        if (!$entity) {
            
            return new JsonResponse([
                'success' => false,
                'code'    => -10,
                'message' => "l'entité n'éxiste pas'",
            ]);
        }
        try {
            $em->remove($entity);
            $em->flush();
            return new JsonResponse([
                'success' => true,
                'message' => 'Entité supprimé',
                'data'    => []
                
            ]);

        } catch (\Exception $exception) {

            return new JsonResponse([
                'success' => false,
                'code'    => $exception->getCode(),
                'message' => $exception->getMessage(),
            ]);
        }
        $em->remove($entity);
        $em->flush();
        
    }

}
