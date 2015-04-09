<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class VmTaxrefHierarchieRepository extends EntityRepository {
    
    public function findLimitedTaxrefHierarchie($limit = 50 , $where, $qparameters) {
        $fieldListeQry = $this->createQueryBuilder('VmTaxrefHierarchie')
            ->setMaxResults($limit);
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
}
