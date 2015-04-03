<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\BibFiltres;

use JSM\Serializer\SerializerBuilder;


class BibFiltresController extends Controller
{
    public function getAction()
    {
        $em = $this->getDoctrine()->getManager();
            
        $entities = $em->getRepository('PnXTaxonomieBundle:BibFiltres')->findAll();
        
        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response(  $jsonContent); 
    }
    
    public function getOneAction($id)
    {
        $em = $this->getDoctrine()->getManager();

        $entity = $em->getRepository('PnXTaxonomieBundle:BibFiltres')->find($id);
    
        
        $serializer = $this->get('jms_serializer');
        
        $jsonContent = $serializer->serialize($entity, 'json');
        return new Response(  $jsonContent); 
    }
}
