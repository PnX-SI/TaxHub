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
     * @var \PnX\TaxonomieBundle\Entity\Taxref
     */
    private $cdNom;


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
     * @param \PnX\TaxonomieBundle\Entity\Taxref $cdNom
     * @return BibTaxons
     */
    public function setCdNom(\PnX\TaxonomieBundle\Entity\Taxref $cdNom = null)
    {
        $this->cdNom = $cdNom;

        return $this;
    }

    /**
     * Get cdNom
     *
     * @return \PnX\TaxonomieBundle\Entity\Taxref 
     */
    public function getCdNom()
    {
        return $this->cdNom;
    }
}
