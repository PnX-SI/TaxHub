<?php

namespace PnX\TaxonomieBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * VTaxrefHierarchieBibtaxons
 */
class VTaxrefHierarchieBibtaxons
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
    private $cdRef;

    /**
     * @var string
     */
    private $lbNom;

    /**
     * @var string
     */
    private $idRang;

    /**
     * @var integer
     */
    private $nbTxFm;

    /**
     * @var integer
     */
    private $nbTxOr;

    /**
     * @var integer
     */
    private $nbTxCl;

    /**
     * @var integer
     */
    private $nbTxPh;

    /**
     * @var integer
     */
    private $nbTxKd;


    /**
     * Set cdNom
     *
     * @param integer $cdNom
     * @return VTaxrefHierarchieBibtaxons
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
     * Set regne
     *
     * @param string $regne
     * @return VTaxrefHierarchieBibtaxons
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
     * @return VTaxrefHierarchieBibtaxons
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
     * @return VTaxrefHierarchieBibtaxons
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
     * @return VTaxrefHierarchieBibtaxons
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
     * @return VTaxrefHierarchieBibtaxons
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
     * Set cdRef
     *
     * @param integer $cdRef
     * @return VTaxrefHierarchieBibtaxons
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
     * @return VTaxrefHierarchieBibtaxons
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
     * Set idRang
     *
     * @param string $idRang
     * @return VTaxrefHierarchieBibtaxons
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
     * Set nbTxFm
     *
     * @param integer $nbTxFm
     * @return VTaxrefHierarchieBibtaxons
     */
    public function setNbTxFm($nbTxFm)
    {
        $this->nbTxFm = $nbTxFm;

        return $this;
    }

    /**
     * Get nbTxFm
     *
     * @return integer 
     */
    public function getNbTxFm()
    {
        return $this->nbTxFm;
    }

    /**
     * Set nbTxOr
     *
     * @param integer $nbTxOr
     * @return VTaxrefHierarchieBibtaxons
     */
    public function setNbTxOr($nbTxOr)
    {
        $this->nbTxOr = $nbTxOr;

        return $this;
    }

    /**
     * Get nbTxOr
     *
     * @return integer 
     */
    public function getNbTxOr()
    {
        return $this->nbTxOr;
    }

    /**
     * Set nbTxCl
     *
     * @param integer $nbTxCl
     * @return VTaxrefHierarchieBibtaxons
     */
    public function setNbTxCl($nbTxCl)
    {
        $this->nbTxCl = $nbTxCl;

        return $this;
    }

    /**
     * Get nbTxCl
     *
     * @return integer 
     */
    public function getNbTxCl()
    {
        return $this->nbTxCl;
    }

    /**
     * Set nbTxPh
     *
     * @param integer $nbTxPh
     * @return VTaxrefHierarchieBibtaxons
     */
    public function setNbTxPh($nbTxPh)
    {
        $this->nbTxPh = $nbTxPh;

        return $this;
    }

    /**
     * Get nbTxPh
     *
     * @return integer 
     */
    public function getNbTxPh()
    {
        return $this->nbTxPh;
    }

    /**
     * Set nbTxKd
     *
     * @param integer $nbTxKd
     * @return VTaxrefHierarchieBibtaxons
     */
    public function setNbTxKd($nbTxKd)
    {
        $this->nbTxKd = $nbTxKd;

        return $this;
    }

    /**
     * Get nbTxKd
     *
     * @return integer 
     */
    public function getNbTxKd()
    {
        return $this->nbTxKd;
    }
}
