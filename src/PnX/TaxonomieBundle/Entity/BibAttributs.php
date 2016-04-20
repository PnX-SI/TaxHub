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
     * @var string
     */
    private $regne;

    /**
     * @var string
     */
    private $group2Inpn;

    /**
     * @var \Doctrine\Common\Collections\Collection
     */
    private $bib_taxons;

    /**
     * Constructor
     */
    public function __construct()
    {
        $this->bib_taxons = new \Doctrine\Common\Collections\ArrayCollection();
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
     * Set regne
     *
     * @param string $regne
     * @return BibAttributs
     */
    public function setRegne($regne)
    {
        $this->regne = $regne;

        return $this;
    }

    /**
     * Get regne
     *
     * @return string 
     */
    public function getRegne()
    {
        return $this->regne;
    }

    /**
     * Set group2Inpn
     *
     * @param string $group2Inpn
     * @return BibAttributs
     */
    public function setGroup2Inpn($group2Inpn)
    {
        $this->group2Inpn = $group2Inpn;

        return $this;
    }

    /**
     * Get group2Inpn
     *
     * @return string 
     */
    public function getGroup2Inpn()
    {
        return $this->group2Inpn;
    }

    /**
     * Add bib_taxons
     *
     * @param \PnX\TaxonomieBundle\Entity\CorTaxonAttribut $bibTaxons
     * @return BibAttributs
     */
    public function addBibTaxon(\PnX\TaxonomieBundle\Entity\CorTaxonAttribut $bibTaxons)
    {
        $this->bib_taxons[] = $bibTaxons;

        return $this;
    }

    /**
     * Remove bib_taxons
     *
     * @param \PnX\TaxonomieBundle\Entity\CorTaxonAttribut $bibTaxons
     */
    public function removeBibTaxon(\PnX\TaxonomieBundle\Entity\CorTaxonAttribut $bibTaxons)
    {
        $this->bib_taxons->removeElement($bibTaxons);
    }

    /**
     * Get bib_taxons
     *
     * @return \Doctrine\Common\Collections\Collection 
     */
    public function getBibTaxons()
    {
        return $this->bib_taxons;
    }
}
