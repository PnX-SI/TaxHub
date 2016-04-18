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
     * @var string
     */
    private $filtre1;

    /**
     * @var string
     */
    private $filtre2;

    /**
     * @var string
     */
    private $filtre3;

    /**
     * @var string
     */
    private $filtre4;

    /**
     * @var string
     */
    private $filtre5;

    /**
     * @var string
     */
    private $filtre6;

    /**
     * @var string
     */
    private $filtre7;

    /**
     * @var string
     */
    private $filtre8;

    /**
     * @var string
     */
    private $filtre9;

    /**
     * @var string
     */
    private $filtre10;

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
     * Set filtre1
     *
     * @param string $filtre1
     * @return BibTaxons
     */
    public function setFiltre1($filtre1)
    {
        $this->filtre1 = $filtre1;

        return $this;
    }

    /**
     * Get filtre1
     *
     * @return string 
     */
    public function getFiltre1()
    {
        return $this->filtre1;
    }

    /**
     * Set filtre2
     *
     * @param string $filtre2
     * @return BibTaxons
     */
    public function setFiltre2($filtre2)
    {
        $this->filtre2 = $filtre2;

        return $this;
    }

    /**
     * Get filtre2
     *
     * @return string 
     */
    public function getFiltre2()
    {
        return $this->filtre2;
    }

    /**
     * Set filtre3
     *
     * @param string $filtre3
     * @return BibTaxons
     */
    public function setFiltre3($filtre3)
    {
        $this->filtre3 = $filtre3;

        return $this;
    }

    /**
     * Get filtre3
     *
     * @return string 
     */
    public function getFiltre3()
    {
        return $this->filtre3;
    }

    /**
     * Set filtre4
     *
     * @param string $filtre4
     * @return BibTaxons
     */
    public function setFiltre4($filtre4)
    {
        $this->filtre4 = $filtre4;

        return $this;
    }

    /**
     * Get filtre4
     *
     * @return string 
     */
    public function getFiltre4()
    {
        return $this->filtre4;
    }

    /**
     * Set filtre5
     *
     * @param string $filtre5
     * @return BibTaxons
     */
    public function setFiltre5($filtre5)
    {
        $this->filtre5 = $filtre5;

        return $this;
    }

    /**
     * Get filtre5
     *
     * @return string 
     */
    public function getFiltre5()
    {
        return $this->filtre5;
    }

    /**
     * Set filtre6
     *
     * @param string $filtre6
     * @return BibTaxons
     */
    public function setFiltre6($filtre6)
    {
        $this->filtre6 = $filtre6;

        return $this;
    }

    /**
     * Get filtre6
     *
     * @return string 
     */
    public function getFiltre6()
    {
        return $this->filtre6;
    }

    /**
     * Set filtre7
     *
     * @param string $filtre7
     * @return BibTaxons
     */
    public function setFiltre7($filtre7)
    {
        $this->filtre7 = $filtre7;

        return $this;
    }

    /**
     * Get filtre7
     *
     * @return string 
     */
    public function getFiltre7()
    {
        return $this->filtre7;
    }

    /**
     * Set filtre8
     *
     * @param string $filtre8
     * @return BibTaxons
     */
    public function setFiltre8($filtre8)
    {
        $this->filtre8 = $filtre8;

        return $this;
    }

    /**
     * Get filtre8
     *
     * @return string 
     */
    public function getFiltre8()
    {
        return $this->filtre8;
    }

    /**
     * Set filtre9
     *
     * @param string $filtre9
     * @return BibTaxons
     */
    public function setFiltre9($filtre9)
    {
        $this->filtre9 = $filtre9;

        return $this;
    }

    /**
     * Get filtre9
     *
     * @return string 
     */
    public function getFiltre9()
    {
        return $this->filtre9;
    }

    /**
     * Set filtre10
     *
     * @param string $filtre10
     * @return BibTaxons
     */
    public function setFiltre10($filtre10)
    {
        $this->filtre10 = $filtre10;

        return $this;
    }

    /**
     * Get filtre10
     *
     * @return string 
     */
    public function getFiltre10()
    {
        return $this->filtre10;
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
