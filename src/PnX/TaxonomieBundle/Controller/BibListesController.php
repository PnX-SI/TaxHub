<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;


use PnX\TaxonomieBundle\Entity\BibListes;
use PnX\TaxonomieBundle\Entity\CorTaxonListe;
/**
 * BibListes controller.
 *
 */
class BibListesController extends Controller
{

    /**
     * Lists all BibListes entities.
     *
     */
    public function getAllAction()
    {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:BibListes')->findAll();
        
        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent); 
    }
    
      public function getSimpleTaxonListsAction() {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:BibListes')->findAll();
        
        $i = 0;
        foreach ($entities as $entity) {
          $results[$i]['idListe'] = $entity->getIdListe();
          $results[$i]['nomListe'] = $entity->getNomListe();
          $results[$i]['descListe'] = $entity->getDescListe();
          $i++;
        }
        
        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent); 
    }
    /**
     * Finds and displays a BibListes entity.
     *
     */
    public function getOneAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:BibListes')->find($id);
        
        $results['idListe'] = $entity->getIdListe();
        $results['nomListe'] = $entity->getNomListe();
        $results['descListe'] = $entity->getDescListe();
        foreach ($entity->getBibTaxons() as $tax) {
          $results['taxons'][] = $tax->getBibTaxons();
        }
        
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent);  
    }
    
    
    public function getTaxonsForOneListAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:CorTaxonListe')->findTaxonsList($id);
        
        $serializer = $this->get('jms_serializer');
         
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent);  
    }
}
