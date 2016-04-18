<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class VmTaxrefHierarchieRepository extends EntityRepository {
    
    public function findLimitedTaxrefHierarchie($limit = 50 , $where, $qparameters, $join) {
        $fieldListeQry = $this->createQueryBuilder('VmTaxrefHierarchie')
            ->setMaxResults($limit);
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }    
        if (count($join)>0) {
            $fieldListeQry = $fieldListeQry->join('VmTaxrefHierarchie.BibTaxons', 't');
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
}
