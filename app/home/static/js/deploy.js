class ThemeFilesDeploy extends JsForm {
    constructor(options) {
        super(options)
        this.objectId = options.fileId||null;
        this.collectionId = options.collectionId||null;
        this.files = JSON.parse(this.options.selectedFiles);
        this.selectedShop = this.options.selectedShop;
        this.themes = null;
        this.selectedTheme = null;
        this.shops = JSON.parse(this.options.shops);
        this.fileDetails = {};
        this.targetElement = ".jsapp";
        this.render(false)
        window.folderHandler = new FileFolders({collectionId:window.collectionId,files:this.files,noclick:true});
        if (this.activeShop) {
            this.loadThemes(this.activeShop)
        } else {
            this.loaded()
        }
        
    }
    
    loadFolders(collectionId,fileId) {
        document.dispatchEvent(
            new CustomEvent(
                "ywm:folders:load",
                {bubbles:true,detail:{collectionId:collectionId,fileId:fileId}}
            )
        )
    }
    formHeader() {
        return "Deploy Files"
    }
    formContents() {
        return `
            <div class="formRow">
                <div class="formField">
                    <label>Shop Name</label>
                    <select name="shop" required>
                        <option value="">Select Shop</option>
                        ${this.shops.map(shop=>`<option value="${shop.shopId}" ${shop.shopId==this.selectedShop?' selected':''}>${shop.name}</option>`).join("")}
                    </select>
                </div>
                <div class="formField">
                    <label>Theme</label>
                    <select name="themes" class="${this.themes?.length<1?'hidden':''}" required>
                        <option value="">Select theme</option>
                        ${this.themes?.map(theme=>`<option value="${theme.themeId}">${theme.name}</option>`).join("")}
                    </select>
                </div>
            </div>
    `
    }
    buttons() {
        return [
            [
                {type:"submit",label:"Deploy",action:"deploy-files",class:"deploy-files"}
            ]
        ]
    }
    loadThemes(shopId) {
        this.loaded(false);
        this.get(`/shops/themes/${this.selectedShop}`).then(response=>{
            this.themes = response.themeList||[];
            console.error("LOADING themes",this.themes)
            this.render()
        }).catch(e=>{
            console.error("LOADING themes",this.themes)
            this.themes = [];
            this.render()
        })
    }
    setupEvents() {
        super.setupEvents()
        if (this.selectedShop && this.themes==null) {
            
            setTimeout(
                ()=>{
                    console.error(`loading themes ${this.themes}`)
                    this.loadThemes(this.selectedShop);
                }
            )
            
        }
        this.formTarget().querySelector('select[name="shop"]').addEventListener("change",event=>{
            var select = event.target;
            this.selectedShop = select.options[select.selectedIndex].value
            this.loaded(false)
            this.loadThemes(this.selectedShop)
        })
        this.formTarget().querySelector('select[name="themes"]').addEventListener("change",event=>{
            var select = event.target;
        })
        this.listenFor(
            "deploy-files",
            event=>{
                let filesSelected = FileFolders.collectFiles()
                if (filesSelected.length<1) {
                    this.showError("no files selected!");
                    return;
                }
                this.deploy()
            }
        )
    }
    deploy() {
        let getSelectDetail = (selector)=>{
            try {
                let select = document.querySelector(`select[name="${selector}"]`)
                let selectedOption = select.options[select.selectedIndex]
                return {
                    name:selectedOption.textContent,
                    id:selectedOption.value
                };
            } catch(e) {
                return {name:"N/A",id:""}
            }
        };
        let shop = getSelectDetail("shop")
        let theme = getSelectDetail("themes");
        let queue = Array.from(
                document.querySelectorAll('.sidebar-options.files input[name="fileId"]:checked')
            ).map(file=>{
                return {
                    "file":{
                        "name":file.dataset.fileName,
                        "id":file.value
                    },
                    "shop":getSelectDetail("shop"),
                    "theme":getSelectDetail("themes")
                }
            });
        let taskOptions = {
            queue:queue,
            id:"deploy-queue",
            owner:this.formTarget(),
        }
        this.formTarget().addEventListener(
            "deploy-queue-complete",
            event=>{
                this.formTarget().classList.remove("track-progress")
            }
        )
        this.listenFor(
            "deploy-queue-complete",
            (event)=>{
                
            }
        )
        let deployQueue = new DepoymentQueue(taskOptions);
    }
    
    
    handleResponse(response,formData) {
        this.fileDetails = response.fileContents
        this.ojbjectId = this.fileDetails.id;
        this.loadFolders(this.fileDetails.collection,this.fileId)
        document.querySelector("#formHeader").textContent = 
        history.replaceState(null, "", `/files?fileId=${this.fileId}`);
    }
}

class DepoymentQueue extends TaskQueue {
    constructor(options) {
        super(options);
    }
    title() {
        return "Deploying files";
    }
    finalize() {
        this.target.querySelector(".progress-text").textContent = "Deployment Complete"
        console.error("finalizinr")
        setTimeout(()=>{
            console.error("dispatching")
            this.options.owner.dispatchEvent(
                new CustomEvent(
                    `${this.options.id}-complete`
                )
            )
        },1000)

    }
    taskDescription() {
        /*
        if (this.queue.length<1) {
            if(!this.currentItem) {
                return "Starting deployment..."
            }
            return `Deploying files to ${this.currentItem.shop.name} completed`
        }
            */
        if (this.currentItem) {
            return `<div class="headline">deploying ${this.currentItem.file.name}</div> <div class="subtitle">${this.currentItem.shop.name} (${this.currentItem.theme.name})</div>`
        }
        

        return 'Starting deployment...'
        
    }
    processTaskTest(item) {
        
        
        setTimeout(()=>{
            this.nextTask()
        },2000)
    }
    processTask(item) {
        this.post(
            "/deploy/execute",
            {
                fileId:item.file.id,
                shopId:item.shop.id,
                themeId: item.theme.id
            }
        ).then(response=>{
            console.error(response)
            this.nextTask()
        })
    }
    
}