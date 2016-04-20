<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * BibListes
 */
class BibListes
{
    /**
     * @var integer
     */
    private $idListe;

    /**
     * @var string
     */
    private $nomListe;

    /**
     * @var string
     */
    private $descListe;

    /**
     * @var string
     */
    private $picto;

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
     * Get idListe
     *
     * @return integer 
     */
    public function getIdListe()
    {
        return $this->idListe;
    }

    /**
     * Set nomListe
     *
     * @param string $nomListe
     * @return BibListes
     */
    public function setNomListe($nomListe)
    {
        $this->nomListe = $nomListe;

        return $this;
    }

    /**
     * Get nomListe
     *
     * @return string 
     */
    public function getNomListe()
    {
        return $this->nomListe;
    }

    /**
     * Set descListe
     *
     * @param string $descListe
     * @return BibListes
     */
    public function setDescListe($descListe)
    {
        $this->descListe = $descListe;

        return $this;
    }

    /**
     * Get descListe
     *
     * @return string 
     */
    public function getDescListe()
    {
        return $this->descListe;
    }

    /**
     * Set picto
     *
     * @param string $picto
     * @return BibListes
     */
    public function setPicto($picto)
    {
        $this->picto = $picto;

        return $this;
    }

    /**
     * Get picto
     *
     * @return string 
     */
    public function getPicto()
    {
        return $this->picto;
    }

    /**
     * Set regne
     *
     * @param string $regne
     * @return BibListes
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
     * @return BibListes
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
     * @param \PnX\TaxonomieBundle\Entity\CorTaxonListe $bibTaxons
     * @return BibListes
     */
    public function addBibTaxon(\PnX\TaxonomieBundle\Entity\CorTaxonListe $bibTaxons)
    {
        $this->bib_taxons[] = $bibTaxons;

        return $this;
    }

    /**
     * Remove bib_taxons
     *
     * @param \PnX\TaxonomieBundle\Entity\CorTaxonListe $bibTaxons
     */
    public function removeBibTaxon(\PnX\TaxonomieBundle\Entity\CorTaxonListe $bibTaxons)
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
