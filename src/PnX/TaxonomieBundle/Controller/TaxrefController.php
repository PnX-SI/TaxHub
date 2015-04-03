<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

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
    public function indexAction()
    {
        $em = $this->getDoctrine()->getManager();

        $limit = $this->getRequest()->get('limit') ;
        $page = $this->getRequest()->get('page') ;
        $entities = $em->getRepository('PnXTaxonomieBundle:Taxref')->createQueryBuilder('taxref')
            ->setFirstResult($page*$limit)
            ->setMaxResults($limit)
            ->getQuery()
            ->getResult();
        
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($entities, 'json');
        return new Response($jsonContent); 
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
        return new Response($jsonContent); 
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
        $fieldListe = $em->getRepository('PnXTaxonomieBundle:Taxref')->createQueryBuilder('taxref')
        ->select('taxref.'.$field)
        ->where(implode(" AND ", $where))
        ->distinct()
        ->setParameters($qparameters)
        ->getQuery();

        $results= $fieldListe->getResult();
        
        $serializer = $this->get('jms_serializer');
        $jsonContent = $serializer->serialize($results, 'json');
        return new Response(  $jsonContent); // or return it in a Response
        
    }
}
