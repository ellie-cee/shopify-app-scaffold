class GraphQl {
    constructor(options) {
        this.config = options;
        this.api_version="2025-10"
    }
     /* graphql functions */
   async graphql(query,params) {
      return fetch(this.siteUrl(`/api/${this.api_version}/graphql.json`),{
          method:"POST",
          headers:{
            "content-type":"application/json",
            "X-Shopify-Storefront-Access-Token":this.config.graphql_token
            },
            body:JSON.stringify({query:query,variables:params})
          })
          .then(response=>response.json())
    }
    graphql_sync(query,params) {
        let ajax = new XMLHttpRequest();
        ajax.headers = {
            "content-type":"application/json",
            "X-Shopify-Storefront-Access-Token":this.config.graphql_token
        }
        ajax.open("POST",this.siteUrl(`/api/${this.api_version}/graphql.json`),false)
        ajax.setRequestHeader("Content-Type", "application/json");
        ajax.setRequestHeader("X-Shopify-Storefront-Access-Token", storefront_token);
        ajax.send(JSON.stringify({query:query,params:params}));
        return JSON.parse(ajax.responseText);
    }
    gid2id(gid) {
        return parseInt(gid.split("/").pop())
    }
    collapse_query(object) {
        if (object==null) {
            return object;
        }
        switch(object.constructor.name) {
        case "Array":
            return object.map(item=>this.collapse_query(item));
            break;
            case "Object":
                let ret = {};
                Object.keys(object).forEach(key=>{
                    if (object[key]==null) {
                        ret[key] = null;
                        return;
                    }
                    if (object[key].reference) {
                        ret[key] = this.collapse_query(object[key].reference)
                        return;

                    }
                    if (object[key].references) {
                        let all = [];
                        object[key].references.nodes.forEach(ref=>{
                            let crv = {};
                            if (ref.fields) {
                            ref.fields.forEach(field=>{
                                crv[field.key]=this.collapse_query(field.value)
                            })  
                            } else {
                            Object.keys(ref).forEach(field=>{
                                
                                if (ref[field]) {
                                if (ref[field].value) {
                                    crv[field]=this.collapse_query(ref[field].value)    
                                } else {
                                    let newHash = {}
                                    Object.keys(ref[field]).forEach(key=>{
                                    newHash[key] = this.collapse_query(ref[field][key])
                                    });
                                    crv[field] = newHash
                                }
                                
                                
                                } else {
                                crv[field] = null
                                }
                                
                            })
                            }
                            
                            all.push(crv)
                        })
                        object[key] = all;

                    }
                    if (object[key].type && object[key].type=="json") {
                    object[key] = JSON.parse(object[key ])
                    }
                    if (object[key].nodes && object[key].nodes.constructor.name=="Array") {
                        ret[key] = this.collapse_query(object[key].nodes);
                    } else {
                        ret[key] = this.collapse_query(object[key])
                    }
                });
                return ret
                break;
            default:
                if (object) {
                    return object;
                }

                break;
        }
    }
}