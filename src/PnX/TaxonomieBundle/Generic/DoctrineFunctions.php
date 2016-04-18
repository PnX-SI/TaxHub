<?php
namespace PnX\TaxonomieBundle\Generic;

use Doctrine\ORM\EntityManager;

class DoctrineFunctions {

  protected $em;
  
  public function __construct(EntityManager $em) {
      $this->em = $em;
  }
  
  /**
   * 
   * name: getEntityFieldList
   * Fonction permettant de récupérer la liste des champs de l'entité
   * @param $entityName (String) : nom de l'entité doctine
   * @return array[String] : liste des nom de champs
   * 
   */
  public function getEntityFieldList($entityName) {
    $metaData = $this->em->getClassMetadata('PnX\TaxonomieBundle\Entity\\'.$entityName);        
    $fieldsName = array();
    foreach ($metaData->fieldNames as $value) {
        $fieldsName[] = $value;
    }
    return $fieldsName;
  }
}
