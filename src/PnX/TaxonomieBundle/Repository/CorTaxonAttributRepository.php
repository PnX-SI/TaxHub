<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class CorTaxonAttributRepository extends EntityRepository {
  
  
	public function findTaxonsList($id, $value) {
		
        $connection = $this->getEntityManager()->getConnection();
        //@TODO : refaire la requête sql pour pouvoir gérer le cas particulier des familles qui ont le même nom
        $where = "WHERE id_attribut = ".$id;
        if($value != null){
            $where .= " AND valeur_attribut = '".$value."'";
        }
        $statement = $connection->prepare("SELECT b.*, a.nom_attribut, c.valeur_attribut 
            FROM taxonomie.bib_taxons b
            JOIN (SELECT * FROM  taxonomie.cor_taxon_attribut ".$where.") c ON c.id_taxon = b.id_taxon
            JOIN taxonomie.bib_attributs a ON a.id_attribut = c.id_attribut
            ");
        $statement->execute();
        $results = $statement->fetchAll();
        return $results;
	}
    /*
    public function createTaxonAttributsSave($id, $attributs) {
		
        $connection = $this->getEntityManager()->getConnection();

        $statement = $connection->prepare("
            DELETE FROM taxonomie.cor_taxon_attribut WHERE id_taxon = ".$id);
        $statement->execute();
        foreach($attributs as $key => $value){
            $statement = $connection->prepare("
                INSERT INTO taxonomie.cor_taxon_attribut(id_taxon,id_attribut,valeur_attribut) VALUES(".$id.",".$key.",'".$value."')"
            );
            $statement->execute();
        }        

        return $id;
	}
    
    public function createTaxonAttributs($id, $attributs) {
		$em = $this->getDoctrine()->getManager();
        $entities= $em->getRepository('PnXTaxonomieBundle:CorTaxonAttribut')->find($id);
        //on test si le taxon a déjà des attributs ou pas, si oui on delete tous les enregistrements de ce taxon
        if($entities){
            foreach($entities AS $entity){
                $em->remove($entity);
                $em->flush();
            }
        }
        $status = false;
        $code = 200;
        $message = "Attribut ajouté";
        $nbAttributs = 0;
        foreach($attributs as $key => $value){
            $entity = new CorTaxonAttribut();
            $entity->setIdTaxon($id);
            $entity->setIdAttribut($key);
            $entity->setValeurAttribut($value);
            try {
                $em->persist($entity);
                $em->flush();
                $status = true;
                $nbAttributs++;
            } 
            catch (\Exception $exception) {
                $status = false;
                $code = $exception->getCode();
                $message = $exception->getMessage();
            }
        }

        return new JsonResponse([
                    'success' => $status,
                    'code'    => $code,
                    'message' => $message,
                    'nbattribut' => $nbAttributs,
        ]);
	}
    */
}
