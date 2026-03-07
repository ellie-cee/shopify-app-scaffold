class Login extends JsForm {
    constructor(options) {
        super(options)
        this.options = options;
        this.loginState = "login"
        this.loginPayload = {}
        this.render(false)
        this.post(
            "/auth/login/status",
            {}
        ).then(response=>{
            this.loginPayload = response;
            switch(response.status) {
                case 404:
                    this.loginState = "login";
                    break;
                case 200:
                    this.loginState = "verify";
                    break;
                case 302:
                    if (this.options.redirectTo) {
                        location.href = this.options.redirectTo;
                    }
                    location.href = "/";
                    return;
                default:
                   this.loginState = "login"
            }
            this.render()
        })
    }
    
    formName() {
        return "loginForm"
    }
    formContents() {
        if (this.loginState=="login") {
            return  `
            <input type="email" placeholder="Enter your email address" name="email" required="true">
            `
        } else {
            return `
                <input type="text" placeholder="Enter login code" name="authCode" required="true">
            
            `
        }
    }
    buttons() {
        if (this.loginState=="login") {
            return [
                [
                    {label:"Login In",action:"log-in",type:"submit"}
                ]
            ]
        } else {
            return [
                [{label:"Verify",action:"verify-code",type:"submit"}],
                [
                    {"label":"Resend Code",action:"resend-code"},
                    {"label":"User Another Email",action:"restart-login"}
                ]
            ]

        }
    }
    setupEvents() {
        super.setupEvents();
        
        this.listenFor(
            "log-in",
            
            (event)=>{
                this.loaded(false)
                this.post(
                    "/auth/login",
                    this.serializeForm(this.formTarget())
                ).then(response=>{
                    this.loginPayload = response;
                    switch(response.status) {
                        case 200:
                            this.loginState="verify";
                            break;
                        case 302:
                            if (this.options.redirectTo) {
                                location.href = this.options.redirectTo;
                                return;
                            }
                            location.href="/";
                        case 404:
                            this.showError(response.message)
                            break;
                    }
                    this.render()
                });
            }
        );
        this.listenFor(
            "verify-code",
            (event)=>{
                this.loaded(false)
                this.post(
                    "auth/code/validate",
                    this.serializeForm(this.formTarget())
                ).then(response=>{
                        this.loaded()
                        switch(response.status) {
                            case 302:
                                if (this.options.redirectTo) {
                                    location.href = this.options.redirectTo;
                                }
                                location.href = "/";
                                break;
                            case 404:
                                this.showError(response.message);
                                break;
                        }
                    }
                )
            }
        )
        this.listenFor(
            "resend-code",
            (event)=>{
                this.loaded(false)
                this.post(
                    "/auth/code/resend",
                    {}
                ).then(response=>{
                    this.loaded()
                    this.showMessage("code resent")
                })
            }
        )
        this.listenFor(
            "restart-login",
            (event)=>{
                this.loaded(false)
                this.post(
                    "/auth/code/restart",
                    {}
                ).then(response=>{
                    this.loginState = "login"
                    this.render()
                })
            }
        )
    }
    formHeader() {
        if (this.loginState=="login") {
            return "Log In"
        } else {
            return `Please enter the code sent to ${this.loginPayload.userEmail}`
        }
    }
}