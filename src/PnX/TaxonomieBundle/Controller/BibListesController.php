<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\BibListes;

use JSM\Serializer\SerializerBuilder;


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
    public function indexAction()
    {
        $em = $this->getDoctrine()->getManager();

        $entities = $em->getRepository('PnXTaxonomieBundle:BibListes')->findAll();

        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response(  $jsonContent); 
    }

    /**
     * Finds and displays a BibListes entity.
     *
     */
    public function showAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:BibListes')->find($id);

        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($entity, 'json');
        return new Response(  $jsonContent); 
    }
}
