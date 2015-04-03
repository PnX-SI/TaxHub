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
     * Add idTaxon
     *
     * @param \PnX\TaxonomieBundle\Entity\BibTaxons $idTaxon
     * @return BibListes
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
