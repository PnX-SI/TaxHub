<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use PnX\TaxonomieBundle\Entity\Taxref;
use JSM\Serializer\SerializerBuilder;


/**
 * Taxref controller.
 *
 */
class TaxrefController extends Controller
{

    /**
     * Lists all Taxref entities.
     *
     */
    public function indexAction() {
        $em = $this->getDoctrine()->getManager();
        
        $limit = $this->getRequest()->get('limit', 50);
        $page = $this->getRequest()->get('page', 0);
        
        $entities = $em->getRepository('PnXTaxonomieBundle:Taxref')->findAllPaginated($page, $limit);
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
        foreach($getParamsKeys as $index => $key) {
            if ($key==='ilike') {
                $where[]='lower(taxref.'.$field.') like lower(:nom_complet)';
                $qparameters['nom_complet']=$this->getRequest()->get($key).'%';
            }
            else {
                $where[]='taxref.'.$key.'= :'.$key;
                $qparameters[$key]=$this->getRequest()->get($key);
            }
        }

        $em = $this->getDoctrine()->getManager();
        $results= $em->getRepository('PnXTaxonomieBundle:Taxref')->findDistinctValueForOneFieldWithParams($field, $where, $qparameters);


        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response($jsonContent, 200, array('content-type' => 'application/json'));
        
    }
}
