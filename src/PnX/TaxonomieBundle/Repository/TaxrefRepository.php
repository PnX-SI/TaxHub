<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class TaxrefRepository extends EntityRepository {
    
    public function findAllPaginated($page =0, $limit = 50 , $where, $qparameters) {
        $fieldListeQry = $this->createQueryBuilder('taxref')
            ->setFirstResult($page*$limit)
            ->setMaxResults($limit);
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
    
    public function findDistinctValueForOneFieldWithParams($field, $where, $qparameters) {

        $fieldListeQry = $this->createQueryBuilder('taxref')
            ->select('taxref.'.$field)
            ->distinct();
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
    
    public function findSynonymsList($cdRef) {

        $fieldListeQry = $this->createQueryBuilder('taxref')
            ->select(['taxref.cdNom as cd_nom','taxref.nomComplet as nom_complet'])
            ->where('taxref.cdRef = :cd_ref')->setParameters(['cd_ref'=>$cdRef]);
            
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }   

}
