document.addEventListener("DOMContentLoaded", function() {
    /**
     * HomePage - Help section
     */
    class Help {
        constructor($el) {
            this.$el = $el;
            this.$buttonsContainer = $el.querySelector(".help--buttons");
            this.$slidesContainers = $el.querySelectorAll(".help--slides");
            this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
            this.init();

        }

        init() {
            this.events();
        }

        events() {
            /**
             * Slide buttons
             */
            this.$buttonsContainer.addEventListener("click", e => {
                if (e.target.classList.contains("btn")) {
                    this.changeSlide(e);
                }
            });

            /**
             * Pagination buttons
             */
            this.$el.addEventListener("click", e => {
                if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
                    this.changePage(e);
                }
            });
        }

        changeSlide(e) {
            e.preventDefault();
            const $btn = e.target;

            // Buttons Active class change
            [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
            $btn.classList.add("active");

            // Current slide
            this.currentSlide = $btn.parentElement.dataset.id;

            // Slides active class change
            this.$slidesContainers.forEach(el => {
                el.classList.remove("active");

                if (el.dataset.id === this.currentSlide) {
                    el.classList.add("active");
                }
            });
        }

        creationInstitutionDOM = (institutions) => {
            institutions.forEach((institution) => {
                if (institution.type == this.currentSlide) {

                    /**
                     *  Make copy of DOM.
                     */

                    let [leftColumn, title, subTitle, rightColumn, text] = this.institutionDivs

                    let li = document.createElement('li')

                    // Nodes clones.
                    leftColumn = leftColumn.cloneNode();
                    title = title.cloneNode();
                    subTitle = subTitle.cloneNode();
                    rightColumn = rightColumn.cloneNode();
                    text = text.cloneNode();

                    // Left Column.
                    title.innerText = institution.name;
                    subTitle.innerText = institution.description;

                    // Right Column.
                    text.innerText = institution.categories;

                    // Add Columns to List item.
                    li.appendChild(leftColumn);
                    li.appendChild(rightColumn);

                    // Divs with Institution Information.
                    leftColumn.appendChild(title);
                    leftColumn.appendChild(subTitle);
                    rightColumn.appendChild(text);

                    // Expand Container with nodes.
                    this.$institutionsContainer.appendChild(li);

                }
            });
        };

        fetchInstitutions = (page) => {
            // Request Header.
            let headers = {
                'Accept': 'application/json',
                'Content-Type':'application/json',
                'X-Requested-With':'XMLHttpRequest',
                'current-page': page,
                'institution-type': this.currentSlide,
            };

            // Request for institutions.
            fetch("http://127.0.0.1:8000/", {method: "GET", headers: headers})
                .then((response) => {

                    // If response status is ok, return response in json.
                    if (response.ok) {
                        return response.json();
                    }
                })
                .then((data) => {

                    // After successful request, parse response to json format.
                    // Iterate over Li and remove them.
                    let institutions = JSON.parse(data)
                    this.$institutionsContainer.querySelectorAll('li').forEach((item) => {
                        item.remove();
                    });

                    // For each object create Li as Slide id equals Institution Type.
                    this.creationInstitutionDOM(institutions);
                });
        }

        changePage(e) {
            e.preventDefault();
            const page = e.target.dataset.page;

            /**
             * Look for all buttons and remove active status, give it to event target.
             */
            [...e.target.parentElement.parentElement.children].forEach((btn) => {
                btn.firstElementChild.classList.remove('active');
            });
            e.target.classList.add('active');

            /**
             *  Select active container.
             */
            this.$institutionsContainer = e.target.parentElement.parentElement.previousElementSibling
            this.institutionDivs = this.$institutionsContainer.querySelectorAll('li div');

            /**
             *  Fetch for pivotal data.
             */
            this.fetchInstitutions(page);

            };
        }

    const helpSection = document.querySelector(".help");
    if (helpSection !== null) {
        new Help(helpSection);
    }

    /**
     * Form Select
     */
    class FormSelect {
        constructor($el) {
            this.$el = $el;
            this.options = [...$el.children];
            this.init();
        }

        init() {
            this.createElements();
            this.addEvents();
            this.$el.parentElement.removeChild(this.$el);
        }

        createElements() {
            // Input for value
            this.valueInput = document.createElement("input");
            this.valueInput.type = "text";
            this.valueInput.name = this.$el.name;

            // Dropdown container
            this.dropdown = document.createElement("div");
            this.dropdown.classList.add("dropdown");

            // List container
            this.ul = document.createElement("ul");

            // All list options
            this.options.forEach((el, i) => {
                const li = document.createElement("li");
                li.dataset.value = el.value;
                li.innerText = el.innerText;

                if (i === 0) {
                    // First clickable option
                    this.current = document.createElement("div");
                    this.current.innerText = el.innerText;
                    this.dropdown.appendChild(this.current);
                    this.valueInput.value = el.value;
                    li.classList.add("selected");
                }

                this.ul.appendChild(li);
            });

            this.dropdown.appendChild(this.ul);
            this.dropdown.appendChild(this.valueInput);
            this.$el.parentElement.appendChild(this.dropdown);
        }

        addEvents() {
            this.dropdown.addEventListener("click", e => {
                const target = e.target;
                this.dropdown.classList.toggle("selecting");

                // Save new value only when clicked on li
                if (target.tagName === "LI") {
                    this.valueInput.value = target.dataset.value;
                    this.current.innerText = target.innerText;
                }
            });
        }
    }
    document.querySelectorAll(".form-group--dropdown select").forEach(el => {
        new FormSelect(el);
    });

    /**
     * Hide elements when clicked on document
     */
    document.addEventListener("click", function(e) {
        const target = e.target;
        const tagName = target.tagName;

        if (target.classList.contains("dropdown")) return false;

        if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
            return false;
        }

        if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
            return false;
        }

        document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
            el.classList.remove("selecting");
        });
    });

    /**
     * Switching between form steps
     */
    class FormSteps {
        constructor(form) {
            this.$form = form;
            this.$next = form.querySelectorAll(".next-step");
            this.$prev = form.querySelectorAll(".prev-step");
            this.$step = form.querySelector(".form--steps-counter span");
            this.currentStep = 1;

            this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
            const $stepForms = form.querySelectorAll("form > div");
            this.slides = [...this.$stepInstructions, ...$stepForms];


            this.init();
        }

        /**
         * Init all methods
         */
        init() {
            this.events();
            this.updateForm();
        }

        /**
         * All events that are happening in form
         */
        events() {
            // Next step
            this.$next.forEach(btn => {
                btn.addEventListener("click", e => {
                    e.preventDefault();
                    this.currentStep++;
                    this.updateForm();
                });
            });

            // Previous step
            this.$prev.forEach(btn => {
                btn.addEventListener("click", e => {
                    e.preventDefault();
                    this.currentStep--;
                    this.updateForm();
                });
            });

            // Form submit
            this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));
        }

        /**
         * Update form front-end
         * Show next or previous section etc.
         */
        updateForm() {
            this.$step.innerText = this.currentStep;

            // TODO: Validation

            this.slides.forEach(slide => {
                slide.classList.remove("active");

                if (slide.dataset.step == this.currentStep) {
                    slide.classList.add("active");
                }
            });

            this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
            this.$step.parentElement.hidden = this.currentStep >= 6;

            // TODO: get data from inputs and show them in summary
        }

        /**
         * Submit form
         *
         * TODO: validation, send data to server
         */
        submit(e) {
            e.preventDefault();
            const form = document.getElementById("donation_form");
            form.submit();
            this.currentStep++;
            this.updateForm();
        }
    }
    const form = document.querySelector(".form--steps");
    if (form !== null) {
        new FormSteps(form);
    }


});
