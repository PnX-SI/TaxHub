<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * CorTaxonAttribut
 */
class CorTaxonAttribut
{
    /**
     * @var integer
     */
    private $idAttribut;

    /**
     * @var integer
     */
    private $idTaxon;

    /**
     * @var string
     */
    private $valeurAttribut;


    /**
     * Set idAttribut
     *
     * @param integer $idAttribut
     * @return CorTaxonAttribut
     */
    public function setIdAttribut($idAttribut)
    {
        $this->idAttribut = $idAttribut;

        return $this;
    }

    /**
     * Get idAttribut
     *
     * @return integer 
     */
    public function getIdAttribut()
    {
        return $this->idAttribut;
    }

    /**
     * Set idTaxon
     *
     * @param integer $idTaxon
     * @return CorTaxonAttribut
     */
    public function setIdTaxon($idTaxon)
    {
        $this->idTaxon = $idTaxon;

        return $this;
    }

    /**
     * Get idTaxon
     *
     * @return integer 
     */
    public function getIdTaxon()
    {
        return $this->idTaxon;
    }

    /**
     * Set valeurAttribut
     *
     * @param string $valeurAttribut
     * @return CorTaxonAttribut
     */
    public function setValeurAttribut($valeurAttribut)
    {
        $this->valeurAttribut = $valeurAttribut;

        return $this;
    }

    /**
     * Get valeurAttribut
     *
     * @return string 
     */
    public function getValeurAttribut()
    {
        return $this->valeurAttribut;
    }
}
