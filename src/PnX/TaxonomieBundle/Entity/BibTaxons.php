<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * BibTaxons
 */
class BibTaxons
{
    /**
     * @var integer
     */
    private $idTaxon;

    /**
     * @var string
     */
    private $nomLatin;

    /**
     * @var string
     */
    private $nomFrancais;

    /**
     * @var string
     */
    private $auteur;

    /**
     * @var integer
     */
    private $cdNom;

    /**
     * @var \PnX\TaxonomieBundle\Entity\Taxref
     */
    private $taxref;


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
     * Set nomLatin
     *
     * @param string $nomLatin
     * @return BibTaxons
     */
    public function setNomLatin($nomLatin)
    {
        $this->nomLatin = $nomLatin;

        return $this;
    }

    /**
     * Get nomLatin
     *
     * @return string 
     */
    public function getNomLatin()
    {
        return $this->nomLatin;
    }

    /**
     * Set nomFrancais
     *
     * @param string $nomFrancais
     * @return BibTaxons
     */
    public function setNomFrancais($nomFrancais)
    {
        $this->nomFrancais = $nomFrancais;

        return $this;
    }

    /**
     * Get nomFrancais
     *
     * @return string 
     */
    public function getNomFrancais()
    {
        return $this->nomFrancais;
    }

    /**
     * Set auteur
     *
     * @param string $auteur
     * @return BibTaxons
     */
    public function setAuteur($auteur)
    {
        $this->auteur = $auteur;

        return $this;
    }

    /**
     * Get auteur
     *
     * @return string 
     */
    public function getAuteur()
    {
        return $this->auteur;
    }

    /**
     * Set cdNom
     *
     * @param integer $cdNom
     * @return BibTaxons
     */
    public function setCdNom($cdNom)
    {
        $this->cdNom = $cdNom;

        return $this;
    }

    /**
     * Get cdNom
     *
     * @return integer 
     */
    public function getCdNom()
    {
        return $this->cdNom;
    }

    /**
     * Set taxref
     *
     * @param \PnX\TaxonomieBundle\Entity\Taxref $taxref
     * @return BibTaxons
     */
    public function setTaxref(\PnX\TaxonomieBundle\Entity\Taxref $taxref = null)
    {
        $this->taxref = $taxref;

        return $this;
    }

    /**
     * Get taxref
     *
     * @return \PnX\TaxonomieBundle\Entity\Taxref 
     */
    public function getTaxref()
    {
        return $this->taxref;
    }
}
