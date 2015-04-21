//je ne comprends pas encore comment injecter ça dans les controller pour utiliser ce service
 
  
app.factory('configService', function () {
  return {
    txConfig : {
        "filter0":
        {
            "name":"patrimonial"
            ,"label1":"taxons patrimoniaux"
            ,"label2":"patrimonilité"
            ,"label2":"test"  
        }
        ,"filter1":
        {
            "name":"protection"
            ,"label1":"taxons protégés"
            ,"label2":"protection"
            ,"label2":"Taxons bénéficiant d'une protection stricte"  
        }
    },
    gettxConfig : function() {
      return this.txConfig;
    }
  }
});
