class ContactForm extends JsForm {
    constructor(options) {
        super(options)
        this.options = options;
        this.sent = false;
        this.render()
    }
    
    formName() {
        return "contactForm"
    }
    formContents() {
        if (this.sent) {
            return `<h2>I'll get back to you as soon possible :)</h2>
                <input type="hidden" name="email-sent" value="1">
            `
        } else {
            return `
                <div class="formrow">
                    <div class="formField">
                        <label>Your Name</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="formField">
                        <label>Your Email</label>
                        <input type="email" name="email" required>
                    </div>
                </div>
                <div class="formrow">
                    <div class="formField">
                        <label>
                            How may I be of assistance?
                        </label>
                        <select name="purpose" required>
                            <option value="">Select</option>
                            <option value="I have a project">I have a project you might be interested in</option>
                            <option value="I have questions about your availability">I have questions about your availability</option>
                            <option value="Some other reason">Some other reason</option>
                            <option value="I want to make fun of your hair">I want to make fun of your hair</option>
                        </select>
                    </div>
                </div>
                <div class="formrow">
                    <div class="formField">
                        <label>
                            Let's hear it!
                        </label>
                        <textarea name="message" rows="10" placeholder="be as wordy as you want to" required></textarea>
                    </div class="formField">
                </div class="formrow">
            `
        }
    }
    buttons() {
        return [
            [
                {label:"Send Message",action:"send-message",type:"submit",class:"for-unsent"}
            ]
        ]
        
    }
    setupEvents() {
        super.setupEvents();
        
        this.listenFor(
            "send-message",
            (event)=>{
                console.error("sending")
                document.dispatchEvent(
                    new CustomEvent(
                    "abc:contact:loading",
                        {}
                    )
                )
                fetch(
                  "https://abc.apps.elliecee.xyz/contact/send",
                    {
                        method:"POST",
                        headers:{
                        "Content-Type":"application/json"
                        },
                        body:JSON.stringify(this.serializeForm(this.formTarget()))  
                    }
                ).then(response=>{
                    this.loginPayload = response;
                    this.loaded()
                    switch(response.status) {
                        case 200:
                            this.sent = true;
                            document.dispatchEvent(
                                new CustomEvent(
                                    "abc:contact:sent",
                                    {}
                                )
                            )
                            break;
                        case 204:
                            this.showError("Unable to send right now? Please try again later. In the meantime, this has been logged. Sorry!")
                        case 404:
                            this.showError(response.message)
                            break;
                    }
                }).catch(error=>{
                    this.showError("Unable to send right now? Please try again later. In the meantime, this has been logged. Sorry!")
                    console.error(error);
                })

                    
            }
        );
    }
    formHeader() {
        if (this.sent) {
            document.dispatchEvent(
                new CustomEvent(
                    "abc:contact:sent",
                    {}
                )
            )
            return "Thank you!"
        } else {
            return `Contact Ellie`
        }
    }
}