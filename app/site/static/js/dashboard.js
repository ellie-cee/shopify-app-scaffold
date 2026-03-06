class Dashboard extends JsForm {
    constructor(options) {
        super(options);
        this.queue = [
            "loadSites",
        ]
        this.nextSlot()
    }
    nextSlot() {
        if (this.queue.length<1) {
            return;
        }
        this.addLoadingCell()
        let nextFunction = this.queue.shift()
        this[nextFunction]()
    }
    loadIntoSlot(element) {
        document.querySelectorAll(".dashboardCell.temporary").forEach(cell=>{
            cell.parentNode.removeChild(cell)
        })
        
        document.querySelector(".dashboard").appendChild(element)
    }
    addLoadingCell() {
        let container = document.createElement("div")
        container.classList.add("temporary")
        container.classList.add("dashboardCell")
        container.innerHTML = `<img src="/static/img/loading.gif" class="dashboard-cell-loading">`
        this.loadIntoSlot(container)
    }
    loadSites() {
        this.get(
            "/shops/list"
        ).then(response=>{
            console.error(response)
            if (response.shopList.length>0) {
                
                let container = this.createCell( `
                    <form id="shopForm">
                        <select name="shops" required>
                            <option value="">Select Shop</option>
                            ${response.shopList.map(shop=>`<option value="${shop.id}">${shop.shopName}`).join("\n")}
                        </select>
                    
                        <div class="formfooter hidden">
                            <div class="buttons">
                                <button class="crud-button">Edit</button>
                                <button type="button" class="upload-button">Update Theme</button>
                            </div>
                        </div>
                    </form>
                    `,
                    "Shops"
                )
                container.querySelector("select").addEventListener("change",event=>{
                    container.querySelector(".formfooter").classList.remove("hidden")
                    }
                )
                let form = container.querySelector("form");
                form.addEventListener("submit",event=>{
                    event.preventDefault()
                    event.stopPropagation()
                    let formData = this.serializeForm(event.target);  
                    location.href=`/shops?shopId=${formData.shops}`
                })
                this.nextSlot()
            }
        })
    }
    createCell(content,title) {
        let container = document.createElement("div")
        container.classList.add("dashboardCell")
        container.innerHTML = `
            <div class="label">${title}</div>
            ${content}
        `;
        this.loadIntoSlot(container)
        return container
    }
    loadThemes() {
        this.get(
            "/shops/themes"
        ).then(response=>{
            console.error(response)
            if (response.shopList.length>0) {
                this.createCell(
                    `
                    <form id="shopForm">
                        <select name="themes" required>
                            <option value="">Select Theme</option>
                            ${response.shopList.map(shop=>`<option value="${shop.id}">${shop.name}`).join("\n")}
                        </select>
                    </form>
                `,
                "Themes"
                )
                this.nextSlot()
            }
        })
    }
}
