class GraphQl {
    defaults() {
        return {
            "debug":true,
            "injection_point":".Esc-app",
        };
    }
    constructor() {
        this.api_version = "2025-10"
    }
    constructUrl(path) {
        let rp = null;
        if (this.options.appHost) {
            rp =  `${location.protocol}//${this.options.appHost}${path}`
        } else {
            rp =  path;
        }
        console.error(rp);
        return rp;
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
class Esc { 
    async get(url) {
        return fetch(
            url,
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                },
            }
        ).then(response=>response.json())
    }
    async postRaw(url,body) {
        try {
        return fetch(
            url,
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                },
                body:body
            }
        )
        } catch(e) {
            console.error(e)
        }
    }
    async post(url,payload) {
        return this.postRaw(
            url,
            JSON.stringify(payload)
        ).then(response=>response.json())
    }
    


    gid2id(gid) {
        return parseInt(gid.split("/").pop())
    }
}

class EscModal extends Esc {
    static show(content,config={}) {
        let modal = document.querySelector(".esc-modal");
        if (!modal) {
            modal = document.createElement("DIV");
            modal.classList.add("esc-modal");
            document.querySelector("body").appendChild(modal);
        }
        modal.style.width = `${window.innerWidth}px`;
        modal.style.height = `${window.innerHeight}px`;
        modal.style.top = `${window.scrollY}px`
        modal.innerHTML = `
        <div class="modal-content">
            <span class="close">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none" role="presentation"><path d="M5.86123 14.1073L5.21766 14.1073L3.67204 12.5617L3.67204 11.9181L6.68057 8.90959L3.6521 5.88112L3.6521 5.23755L5.2376 3.65205L5.88117 3.65204L8.90964 6.68052L11.9182 3.67199L12.5617 3.67199L14.1074 5.21761L14.1074 5.86118L11.0988 8.86971L14.1273 11.8982L14.1273 12.5417L12.5418 14.1273H11.8982L8.86976 11.0988L5.86123 14.1073Z" fill="#af3939"></path></svg>
            </span>
            <div class="modal-text text-left color-foreword-primary body1">
                ${content}
            </div>
        </div>
        `;
        if (config.cantClose){
            modal.querySelector(".close").style.display="none";
        } else {
          modal.querySelector(".close").style.display="block";
          modal.querySelector(".close").addEventListener("click",event=>{
              modal.classList.remove("active");
              modal.innerHTML = "";
              document.querySelector("body").classList.remove("stop-scrolling");
              document.dispatchEvent(new CustomEvent("esc:modal:closed",{bubbles:true}))
          });
          modal.addEventListener("click",event=>{
            if (event.target.classList.contains("esc-modal")) {
                modal.classList.remove("active");
                modal.style.top = "0px";
                modal.innerHTML = "";
                document.querySelector("body").classList.remove("stop-scrolling");
                document.dispatchEvent(new CustomEvent("esc:modal:closed",{bubbles:true}))
                if(config.onClose) {
                    
                    config.onClose()
                }
            }
          })
        } 
        document.querySelector("body").classList.add("stop-scrolling");
        modal.classList.add("active");
        return modal;
    }
    static close() {
    let modal = document.querySelector(".esc-modal");
    modal.classList.remove("active");
    modal.innerHTML = "";
    document.querySelector("body").classList.remove("stop-scrolling");
    return modal
    }
}

class JsForm extends Esc {
    constructor(options) {
        super(options);
        this.uuid = crypto.randomUUID()
        this.options=options;
        this.targetElement = ".jsapp";
        this.listeners = [];
        this.objectId = options.objectId||null;
    }
    messageElement() {
        return document.querySelector(".request-response")
    }
    disappear() {
        this.target().innerHTML = ``;
    }
    showError(message) {
        let footer = this.messageElement()
        footer.classList.add("error")
        footer.textContent=message;
    }
    showMessage(message) {
        let footer = this.messageElement()
        footer.classList.remove("error")
        footer.textContent=message;
    }
    serializeForm(form) {
        return Object.fromEntries(new FormData(form).entries())
    }
    target() {
        
        return document.querySelector(this.targetElement);
    }
    formName() {
        return "form"
    }
    formTarget() {

        return document.querySelector(`#${this.formName()}`)
    }
    formHeader() {
        return "a form"
    }
    buttons() {
        return []
    }
    subtitle() {
        return ''
    }
    hasObjectId() {
        return (this.objectId!=null && this.objectId!="");
    }
    hostFor() {
        let params = new URLSearchParams(location.search);
    }
    
    render(isLoaded=true) {
        this.target().innerHTML = `
            <form id="${this.formName()}" class="jsform ${isLoaded?'loaded':''}">
                <div class="form-loading">
                    <img src="${this.constructUrl('/static/img/loading.gif')}">
                </div>
                <div class="form-progress"></div>
                <div class="form-header-wrapper">
                    <h1 id="formHeader">
                        ${this.formHeader()}
                    </h1>
                </div>
                <div class="subtitle">${this.subtitle()}</div>
                <div class="request-response"></div>
                
                <div class="formBody">
                    ${this.formContents()}
                </div> 
                <div class="formfooter">
                    ${this.buttons().map(row=>`
                        <div class="buttons">
                            ${row.map(button=>`
                            <button class="${button.class?button.class:''}" data-action="${button.action}" type="${button.type?button.type:'button'}">
                                ${button.label}
                            </button>
                            `
                        ).join("")}
                        </div>
                        `
                    ).join("")}
                </div>
            </form>
        `
        if (this.hasObjectId()) {
            this.setObjectId(this.objectId)
        }
        
        this.setupEvents();
    }
    formContents() {
        return "blorp"
    }
    eventsPrefix() {
        return `ywm:${this.formName()}`
    }
    eventName(eventName) {
        return `${this.eventsPrefix()}:${eventName}`
    }
    listenFor(eventName,callBack=null) {
        
        
        
        this.listeners.push(eventName)
        this.formTarget().addEventListener(
            this.eventName(eventName),
            event=>{
                
                if (callBack) {
                    callBack(event);
                }
                event.stopPropagation()
            }
        )
    }
    showMessage(message,isError=false) {
        let notyf = new Notyf(
            {
                ripple:true,
                duration:3000,
                position:{x:'right',y:'center'}
            }
        );
        notyf.success(message);
    }
    showError(message,permanent=false) {

        let notyf = null;
        if (!permanent) {
            notyf =  new Notyf({
                    ripple:true,
                    duration:5000,
                    position:{x:'right',y:'center'}
                }
            );
        } else {
            notyf =  new Notyf(
                {
                    ripple:true,
                    position:{x:'right',y:'center'}
                }
            );
        }
        notyf.error(message)
    }
    loading() {
        this.loaded(false)
    }
    loaded(loaded=true) {
        
        if (loaded) {
            this.formTarget().classList.add("loaded")
        } else {
            this.formTarget().classList.remove("loaded")
        }
    }
    proxyUrlFor(path) {
        let params = new URLSearchParams(location.search)
        console.error(params)
        if (params.get("shop") && params.get("signature")) {
            return `/apps/xyz/${path}`
            
        } else {
            return `/shopify-proxy/${path}`
        }
    }
    dispatchEvent(thisEventName,detail=null) {
        
        this.formTarget().dispatchEvent(
            new CustomEvent(
                thisEventName,
                {bubbles:true,detail:detail}
            )
        )
    }
    setupEvents() {
        
        let form = this.formTarget()
        form.addEventListener("submit",event=>{
            event.preventDefault();
            event.stopPropagation();

            let submitAction =this.formTarget().querySelector(`button[type="submit"]`).dataset.action;
            this.dispatchEvent(this.eventName(submitAction));
            event.stopPropagation()
            return;
        })
        this.formTarget().querySelectorAll("button[data-action]").forEach(button=>{
            
            if (button.type=="submit") {
                return;
            }
            button.addEventListener("click",event=>{
                
                this.dispatchEvent(this.eventName(button.dataset.action))
                event.stopPropagation()
            })
        });
        this.formTarget().querySelectorAll(".peeker").forEach(peeker=>peeker.addEventListener("click",event=>{
            let input = document.querySelector(`input[name="${peeker.dataset.for}"]`)

            if (input.type=="password") {
                input.type="text";
            } else {
                input.type="password";
            }
            }));
        
        this.formTarget().querySelectorAll("textarea").forEach(textArea=>{
            textArea.addEventListener("keydown",event=> {
                if (event.key=="Tab") {
                    event.preventDefault();
                    let position = textArea.selectionStart;
                    
                    let text = textArea.value;    
                    textArea.value = text.slice(0, position) + "   " + text.slice(position);
                }
            })
        })
    }
    setObjectId(id) {
        if (id==null) {
            return
        }
        this.fileId = id;
        let form  = document.querySelector(`#${this.formName()}`)
        let idInput = form.querySelector('[name="objectId]')
        if (idInput!=null) {
            idInput.value = id;
        } else {
            let input = document.createElement("input");
            input.type="hidden";
            input.name="objectId";
            input.value = id;
            form.appendChild(input)
        }
    }
    constructUrl(path) {
        let rp = null;
        if (this.options.appHost) {
            rp =  `${location.protocol}//${this.options.appHost}${path}`
        } else {
            rp =  path;
        }
        console.error(rp);
        return rp;
    }

}

class TaskQueue extends JsForm {
    constructor(options) {
        super(options);
        this.options = options;
        this.processedItems = [];
        this.queue = this.options.queue;
        this.queueLength = this.queue.length;
        this.currentItem = null;
        this.target = this.options.owner.querySelector(".form-progress");
        this.toggleVisibility()
        this.nextTask()
        

    }
    
    toggleVisibility() {
        let form = this.options.owner;
        form.classList.toggle("track-progress")
    }
    finalize() {

    }
    nextTask() {
        this.render()
        if (this.queue.length<1) {
            setTimeout(
                ()=>{
                    this.finalize()
                },
                1000
            )
            return;
        }
        
        this.currentItem = this.queue.shift();
        
        if (this.currentItem) {
            
            this.processedItems.push(this.currentItem)
        }
        this.processTask(this.currentItem)
    }
    processTask(currentItem) {
        this.nextTask()
    }
    taskDescription() {
        return '';
    }
    title() {
        return '';
    }
    queueProgressPercent() {
        return Math.ceil((this.processedItems.length/this.queueLength)*100);
    }
    render() {
        
        this.target.innerHTML = ` 
            <div class="progress-box">
                <div class="content">
                    <h3>${this.title()}</h3>
                    <div class="progress-bar">
                        <div class="inner" style="width:${this.queueProgressPercent()}%"></div>
                    </div>
                    <div class="progress-text">
                        ${this.taskDescription()}
                    </div>
                </div>
            </div>
        `
    }
}

