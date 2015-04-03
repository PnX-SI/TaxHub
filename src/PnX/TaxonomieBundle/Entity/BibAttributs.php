<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * BibAttributs
 */
class BibAttributs
{
    /**
     * @var integer
     */
    private $idAttribut;

    /**
     * @var string
     */
    private $nomAttribut;

    /**
     * @var string
     */
    private $labelAttribut;

    /**
     * @var string
     */
    private $listeValeurAttribut;

    /**
     * @var boolean
     */
    private $obligatoire;

    /**
     * @var string
     */
    private $descAttribut;

    /**
     * @var string
     */
    private $typeAttribut;

    /**
     * @var \Doctrine\Common\Collections\Collection
     */
    private $idTaxon;

    /**
     * Constructor
     */
    public function __construct()
    {
        $this->idTaxon = new \Doctrine\Common\Collections\ArrayCollection();
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
     * Set nomAttribut
     *
     * @param string $nomAttribut
     * @return BibAttributs
     */
    public function setNomAttribut($nomAttribut)
    {
        $this->nomAttribut = $nomAttribut;

        return $this;
    }

    /**
     * Get nomAttribut
     *
     * @return string 
     */
    public function getNomAttribut()
    {
        return $this->nomAttribut;
    }

    /**
     * Set labelAttribut
     *
     * @param string $labelAttribut
     * @return BibAttributs
     */
    public function setLabelAttribut($labelAttribut)
    {
        $this->labelAttribut = $labelAttribut;

        return $this;
    }

    /**
     * Get labelAttribut
     *
     * @return string 
     */
    public function getLabelAttribut()
    {
        return $this->labelAttribut;
    }

    /**
     * Set listeValeurAttribut
     *
     * @param string $listeValeurAttribut
     * @return BibAttributs
     */
    public function setListeValeurAttribut($listeValeurAttribut)
    {
        $this->listeValeurAttribut = $listeValeurAttribut;

        return $this;
    }

    /**
     * Get listeValeurAttribut
     *
     * @return string 
     */
    public function getListeValeurAttribut()
    {
        return $this->listeValeurAttribut;
    }

    /**
     * Set obligatoire
     *
     * @param boolean $obligatoire
     * @return BibAttributs
     */
    public function setObligatoire($obligatoire)
    {
        $this->obligatoire = $obligatoire;

        return $this;
    }

    /**
     * Get obligatoire
     *
     * @return boolean 
     */
    public function getObligatoire()
    {
        return $this->obligatoire;
    }

    /**
     * Set descAttribut
     *
     * @param string $descAttribut
     * @return BibAttributs
     */
    public function setDescAttribut($descAttribut)
    {
        $this->descAttribut = $descAttribut;

        return $this;
    }

    /**
     * Get descAttribut
     *
     * @return string 
     */
    public function getDescAttribut()
    {
        return $this->descAttribut;
    }

    /**
     * Set typeAttribut
     *
     * @param string $typeAttribut
     * @return BibAttributs
     */
    public function setTypeAttribut($typeAttribut)
    {
        $this->typeAttribut = $typeAttribut;

        return $this;
    }

    /**
     * Get typeAttribut
     *
     * @return string 
     */
    public function getTypeAttribut()
    {
        return $this->typeAttribut;
    }

    /**
     * Add idTaxon
     *
     * @param \PnX\TaxonomieBundle\Entity\BibTaxons $idTaxon
     * @return BibAttributs
     */
    public function addIdTaxon(\PnX\TaxonomieBundle\Entity\BibTaxons $idTaxon)
    {
        $this->idTaxon[] = $idTaxon;

        return $this;
    }

    /**
     * Remove idTaxon
     *
     * @param \PnX\TaxonomieBundle\Entity\BibTaxons $idTaxon
     */
    public function removeIdTaxon(\PnX\TaxonomieBundle\Entity\BibTaxons $idTaxon)
    {
        $this->idTaxon->removeElement($idTaxon);
    }

    /**
     * Get idTaxon
     *
     * @return \Doctrine\Common\Collections\Collection 
     */
    public function getIdTaxon()
    {
        return $this->idTaxon;
    }
}
