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
     * @var \PnX\TaxonomieBundle\Entity\BibAttributs
     */
    private $bib_attributs;

    /**
     * @var \PnX\TaxonomieBundle\Entity\BibTaxons
     */
    private $bib_taxons;


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
     * Set bib_attributs
     *
     * @param \PnX\TaxonomieBundle\Entity\BibAttributs $bibAttributs
     * @return CorTaxonAttribut
     */
    public function setBibAttributs(\PnX\TaxonomieBundle\Entity\BibAttributs $bibAttributs = null)
    {
        $this->bib_attributs = $bibAttributs;

        return $this;
    }

    /**
     * Get bib_attributs
     *
     * @return \PnX\TaxonomieBundle\Entity\BibAttributs 
     */
    public function getBibAttributs()
    {
        return $this->bib_attributs;
    }

    /**
     * Set bib_taxons
     *
     * @param \PnX\TaxonomieBundle\Entity\BibTaxons $bibTaxons
     * @return CorTaxonAttribut
     */
    public function setBibTaxons(\PnX\TaxonomieBundle\Entity\BibTaxons $bibTaxons = null)
    {
        $this->bib_taxons = $bibTaxons;

        return $this;
    }

    /**
     * Get bib_taxons
     *
     * @return \PnX\TaxonomieBundle\Entity\BibTaxons 
     */
    public function getBibTaxons()
    {
        return $this->bib_taxons;
    }
}
