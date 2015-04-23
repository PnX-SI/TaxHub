<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * CorTaxonListe
 */
class CorTaxonListe
{
    /**
     * @var integer
     */
    private $idListe;

    /**
     * @var integer
     */
    private $idTaxon;

    /**
     * @var \PnX\TaxonomieBundle\Entity\BibListes
     */
    private $bib_listes;

    /**
     * @var \PnX\TaxonomieBundle\Entity\BibTaxons
     */
    private $bib_taxons;


    /**
     * Set idListe
     *
     * @param integer $idListe
     * @return CorTaxonListe
     */
    public function setIdListe($idListe)
    {
        $this->idListe = $idListe;

        return $this;
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
     * Set idTaxon
     *
     * @param integer $idTaxon
     * @return CorTaxonListe
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
     * Set bib_listes
     *
     * @param \PnX\TaxonomieBundle\Entity\BibListes $bibListes
     * @return CorTaxonListe
     */
    public function setBibListes(\PnX\TaxonomieBundle\Entity\BibListes $bibListes = null)
    {
        $this->bib_listes = $bibListes;

        return $this;
    }

    /**
     * Get bib_listes
     *
     * @return \PnX\TaxonomieBundle\Entity\BibListes 
     */
    public function getBibListes()
    {
        return $this->bib_listes;
    }

    /**
     * Set bib_taxons
     *
     * @param \PnX\TaxonomieBundle\Entity\BibTaxons $bibTaxons
     * @return CorTaxonListe
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
