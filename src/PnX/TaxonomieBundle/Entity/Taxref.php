<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * Taxref
 */
class Taxref
{
    /**
     * @var integer
     */
    private $cdNom;

    /**
     * @var string
     */
    private $regne;

    /**
     * @var string
     */
    private $phylum;

    /**
     * @var string
     */
    private $classe;

    /**
     * @var string
     */
    private $ordre;

    /**
     * @var string
     */
    private $famille;

    /**
     * @var integer
     */
    private $cdTaxsup;

    /**
     * @var integer
     */
    private $cdSup;

    /**
     * @var integer
     */
    private $cdRef;

    /**
     * @var string
     */
    private $lbNom;

    /**
     * @var string
     */
    private $lbAuteur;

    /**
     * @var string
     */
    private $nomComplet;

    /**
     * @var string
     */
    private $nomCompletHtml;

    /**
     * @var string
     */
    private $nomValide;

    /**
     * @var string
     */
    private $nomVern;

    /**
     * @var string
     */
    private $nomVernEng;

    /**
     * @var string
     */
    private $group1Inpn;

    /**
     * @var string
     */
    private $group2Inpn;

    /**
     * @var string
     */
    private $idHabitat;

    /**
     * @var string
     */
    private $idRang;

    /**
     * @var string
     */
    private $idStatut;


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
     * Set regne
     *
     * @param string $regne
     * @return Taxref
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
     * Set phylum
     *
     * @param string $phylum
     * @return Taxref
     */
    public function setPhylum($phylum)
    {
        $this->phylum = $phylum;

        return $this;
    }

    /**
     * Get phylum
     *
     * @return string 
     */
    public function getPhylum()
    {
        return $this->phylum;
    }

    /**
     * Set classe
     *
     * @param string $classe
     * @return Taxref
     */
    public function setClasse($classe)
    {
        $this->classe = $classe;

        return $this;
    }

    /**
     * Get classe
     *
     * @return string 
     */
    public function getClasse()
    {
        return $this->classe;
    }

    /**
     * Set ordre
     *
     * @param string $ordre
     * @return Taxref
     */
    public function setOrdre($ordre)
    {
        $this->ordre = $ordre;

        return $this;
    }

    /**
     * Get ordre
     *
     * @return string 
     */
    public function getOrdre()
    {
        return $this->ordre;
    }

    /**
     * Set famille
     *
     * @param string $famille
     * @return Taxref
     */
    public function setFamille($famille)
    {
        $this->famille = $famille;

        return $this;
    }

    /**
     * Get famille
     *
     * @return string 
     */
    public function getFamille()
    {
        return $this->famille;
    }

    /**
     * Set cdTaxsup
     *
     * @param integer $cdTaxsup
     * @return Taxref
     */
    public function setCdTaxsup($cdTaxsup)
    {
        $this->cdTaxsup = $cdTaxsup;

        return $this;
    }

    /**
     * Get cdTaxsup
     *
     * @return integer 
     */
    public function getCdTaxsup()
    {
        return $this->cdTaxsup;
    }

    /**
     * Set cdSup
     *
     * @param integer $cdSup
     * @return Taxref
     */
    public function setCdSup($cdSup)
    {
        $this->cdSup = $cdSup;

        return $this;
    }

    /**
     * Get cdSup
     *
     * @return integer 
     */
    public function getCdSup()
    {
        return $this->cdSup;
    }

    /**
     * Set cdRef
     *
     * @param integer $cdRef
     * @return Taxref
     */
    public function setCdRef($cdRef)
    {
        $this->cdRef = $cdRef;

        return $this;
    }

    /**
     * Get cdRef
     *
     * @return integer 
     */
    public function getCdRef()
    {
        return $this->cdRef;
    }

    /**
     * Set lbNom
     *
     * @param string $lbNom
     * @return Taxref
     */
    public function setLbNom($lbNom)
    {
        $this->lbNom = $lbNom;

        return $this;
    }

    /**
     * Get lbNom
     *
     * @return string 
     */
    public function getLbNom()
    {
        return $this->lbNom;
    }

    /**
     * Set lbAuteur
     *
     * @param string $lbAuteur
     * @return Taxref
     */
    public function setLbAuteur($lbAuteur)
    {
        $this->lbAuteur = $lbAuteur;

        return $this;
    }

    /**
     * Get lbAuteur
     *
     * @return string 
     */
    public function getLbAuteur()
    {
        return $this->lbAuteur;
    }

    /**
     * Set nomComplet
     *
     * @param string $nomComplet
     * @return Taxref
     */
    public function setNomComplet($nomComplet)
    {
        $this->nomComplet = $nomComplet;

        return $this;
    }

    /**
     * Get nomComplet
     *
     * @return string 
     */
    public function getNomComplet()
    {
        return $this->nomComplet;
    }

    /**
     * Set nomCompletHtml
     *
     * @param string $nomCompletHtml
     * @return Taxref
     */
    public function setNomCompletHtml($nomCompletHtml)
    {
        $this->nomCompletHtml = $nomCompletHtml;

        return $this;
    }

    /**
     * Get nomCompletHtml
     *
     * @return string 
     */
    public function getNomCompletHtml()
    {
        return $this->nomCompletHtml;
    }

    /**
     * Set nomValide
     *
     * @param string $nomValide
     * @return Taxref
     */
    public function setNomValide($nomValide)
    {
        $this->nomValide = $nomValide;

        return $this;
    }

    /**
     * Get nomValide
     *
     * @return string 
     */
    public function getNomValide()
    {
        return $this->nomValide;
    }

    /**
     * Set nomVern
     *
     * @param string $nomVern
     * @return Taxref
     */
    public function setNomVern($nomVern)
    {
        $this->nomVern = $nomVern;

        return $this;
    }

    /**
     * Get nomVern
     *
     * @return string 
     */
    public function getNomVern()
    {
        return $this->nomVern;
    }

    /**
     * Set nomVernEng
     *
     * @param string $nomVernEng
     * @return Taxref
     */
    public function setNomVernEng($nomVernEng)
    {
        $this->nomVernEng = $nomVernEng;

        return $this;
    }

    /**
     * Get nomVernEng
     *
     * @return string 
     */
    public function getNomVernEng()
    {
        return $this->nomVernEng;
    }

    /**
     * Set group1Inpn
     *
     * @param string $group1Inpn
     * @return Taxref
     */
    public function setGroup1Inpn($group1Inpn)
    {
        $this->group1Inpn = $group1Inpn;

        return $this;
    }

    /**
     * Get group1Inpn
     *
     * @return string 
     */
    public function getGroup1Inpn()
    {
        return $this->group1Inpn;
    }

    /**
     * Set group2Inpn
     *
     * @param string $group2Inpn
     * @return Taxref
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
     * Set idHabitat
     *
     * @param string $idHabitat
     * @return Taxref
     */
    public function setIdHabitat($idHabitat)
    {
        $this->idHabitat = $idHabitat;

        return $this;
    }

    /**
     * Get idHabitat
     *
     * @return string 
     */
    public function getIdHabitat()
    {
        return $this->idHabitat;
    }

    /**
     * Set idRang
     *
     * @param string $idRang
     * @return Taxref
     */
    public function setIdRang($idRang)
    {
        $this->idRang = $idRang;

        return $this;
    }

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
     * Set idStatut
     *
     * @param string $idStatut
     * @return Taxref
     */
    public function setIdStatut($idStatut)
    {
        $this->idStatut = $idStatut;

        return $this;
    }

    /**
     * Get idStatut
     *
     * @return string 
     */
    public function getIdStatut()
    {
        return $this->idStatut;
    }
}
