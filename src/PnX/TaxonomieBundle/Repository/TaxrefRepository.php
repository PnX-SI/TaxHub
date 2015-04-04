<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class TaxrefRepository extends EntityRepository {
    
    public function findAllPaginated($page =0, $limit = 50) {
        $results = $this->createQueryBuilder('taxref')
            ->setFirstResult($page*$limit)
            ->setMaxResults($limit)
            ->getQuery()
            ->getResult();
        return $results;
    }
    
    public function findDistinctValueForOneFieldWithParams($field, $where, $qparameters) {

        $fieldListeQry = $this->createQueryBuilder('taxref')
            ->select('taxref.'.$field)
            ->distinct();
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeRep->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
}
