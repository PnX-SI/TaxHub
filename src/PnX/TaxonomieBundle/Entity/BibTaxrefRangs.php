<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * BibTaxrefRangs
 */
class BibTaxrefRangs
{
    /**
     * @var string
     */
    private $idRang;

    /**
     * @var string
     */
    private $nomRang;


    /**
     * Get idRang
     *
     * @return string 
     */
    public function getIdRang()
    {
        return $this->idRang;
    }

    /**
     * Set nomRang
     *
     * @param string $nomRang
     * @return BibTaxrefRangs
     */
    public function setNomRang($nomRang)
    {
        $this->nomRang = $nomRang;

        return $this;
    }

    /**
     * Get nomRang
     *
     * @return string 
     */
    public function getNomRang()
    {
        return $this->nomRang;
    }
}
