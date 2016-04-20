<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;


use PnX\TaxonomieBundle\Entity\BibAttributs;
use PnX\TaxonomieBundle\Entity\CorTaxonAttribut;
/**
 * BibAttributs controller.
 *
 */
class BibAttributsController extends Controller
{

    /**
     * Lists all BibAttributs entities.
     *
     */
    public function getAllAction()
    {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:BibAttributs')->findAll();
        $i = 0;
        foreach ($entities as $entity) {
          $results[$i]['idAttribut'] = $entity->getIdAttribut();
          $results[$i]['nomAttribut'] = $entity->getNomAttribut();
          $results[$i]['labelAttribut'] = $entity->getLabelAttribut();
          $results[$i]['listeValeurAttribut'] = $entity->getListeValeurAttribut();
          $results[$i]['obligatoire'] = $entity->getObligatoire();
          $results[$i]['descAttribut'] = $entity->getDescAttribut();
          $results[$i]['typeAttribut'] = $entity->getTypeAttribut();
          $results[$i]['regne'] = $entity->getRegne();
          $results[$i]['group2Inpn'] = $entity->getGroup2Inpn();
          $i++;
        }
        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent); 
    }
    
    /**
     * Finds and displays a BibAttributs entity.
     *
     */
    public function getOneAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:BibAttributs')->find($id);
        
        $results['idAttribut'] = $entity->getIdAttribut();
        $results['nomAttribut'] = $entity->getNomAttribut();
        $results['labelAttribut'] = $entity->getLabelAttribut();
        $results['listeValeurAttribut'] = $entity->getListeValeurAttribut();
        $results['obligatoire'] = $entity->getObligatoire();
        $results['descAttribut'] = $entity->getDescAttribut();
        $results['typeAttribut'] = $entity->getTypeAttribut();
        $results['regne'] = $entity->getRegne();
        $results['group2Inpn'] = $entity->getGroup2Inpn();
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent);  
    }
    
    
    public function getTaxonsForOneAttributAction($id, $value)
    {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:CorTaxonAttribut')->findTaxonsList($id, $value);
        
        $serializer = $this->get('jms_serializer');
         
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent);  
    }
    
    public function getAttributsByFiltersAction($regne, $group2inpn)
    {
        $qparameters=[];
        $where = [];
        if($regne != null || $group2inpn != null){
            if($regne != null){
                $where[] = '(BibAttributs.regne = :regne OR BibAttributs.regne IS NULL)';
                $qparameters['regne']=$regne;
            }
            if($group2inpn != null){
                $where[] = '(BibAttributs.group2Inpn = :group2_inpn  OR BibAttributs.regne IS NULL OR BibAttributs.group2Inpn IS NULL)';
                $qparameters['group2_inpn']=$group2inpn;
            }
        }
        
        // Récupération des entités correspondant aux critères
        $em = $this->getDoctrine()->getManager();
        $entities = $em->getRepository('PnXTaxonomieBundle:BibAttributs')->findAllByFilter($where, $qparameters);
        
        $i = 0;
        foreach ($entities as $entity) {
          $results[$i]['idAttribut'] = $entity->getIdAttribut();
          $results[$i]['nomAttribut'] = $entity->getNomAttribut();
          $results[$i]['labelAttribut'] = $entity->getLabelAttribut();
          $results[$i]['listeValeurAttribut'] = $entity->getListeValeurAttribut();
          $results[$i]['obligatoire'] = $entity->getObligatoire();
          $results[$i]['descAttribut'] = $entity->getDescAttribut();
          $results[$i]['typeAttribut'] = $entity->getTypeAttribut();
          $results[$i]['regne'] = $entity->getRegne();
          $results[$i]['group2Inpn'] = $entity->getGroup2Inpn();
          $i++;
        }
        
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
    }
}
