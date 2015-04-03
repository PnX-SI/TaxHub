<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * BibTaxrefStatuts
 */
class BibTaxrefStatuts
{
    /**
     * @var string
     */
    private $idStatut;

    /**
     * @var string
     */
    private $nomStatut;


    /**
     * Get idStatut
     *
     * @return string 
     */
    public function getIdStatut()
    {
        return $this->idStatut;
    }

    /**
     * Set nomStatut
     *
     * @param string $nomStatut
     * @return BibTaxrefStatuts
     */
    public function setNomStatut($nomStatut)
    {
        $this->nomStatut = $nomStatut;

        return $this;
    }

    /**
     * Get nomStatut
     *
     * @return string 
     */
    public function getNomStatut()
    {
        return $this->nomStatut;
    }
}
