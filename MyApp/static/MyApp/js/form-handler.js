document.addEventListener("DOMContentLoaded", function() {

    /**
     * Form nav buttons
     */
    const FirstFormNextButton = document.querySelector("div[data-step='1'] button.next-step");
    const SecondFormPrevButton = document.querySelector("div[data-step='2'] button.prev-step");
    const ThirdFormNextButton = document.querySelector("div[data-step='3'] button.next-step");
    FirstFormNextButton.style.display = 'None'
    ThirdFormNextButton.style.display = 'None'

    /**
     * Collect all categories ids when checked.
     */

    let categoriesId = [];
    let categoriesNames = [];
    const categoriesCheckBoxes = (document.querySelectorAll(".form-group--checkbox input[name=categories]"));
    categoriesCheckBoxes.forEach((category) => {



        if (category.checked) {
            categoriesId.push(Number(category.value));
        }

        category.addEventListener('change', () => {

            const categoryName = category.parentElement.querySelector("span.description").innerText
            const categoryId = Number(category.value);

            if (category.checked) {
                categoriesId.push(categoryId);
                categoriesNames.push(` ${categoryName}`)
                FirstFormNextButton.style.display = "block"

            } else {
                const removeCategory = categoriesId.indexOf(categoryId);
                const removeCategoryName = categoriesNames.indexOf(categoryName)
                categoriesId.splice(removeCategory, 1);
                categoriesNames.splice(removeCategoryName, 1);

                if (categoriesId.length <= 0) {
                    FirstFormNextButton.style.display = 'None'
                }
            }

        });

    });


    // /* Compare arrays */
    // const compareArrays = (a, b) => {
    //     a.sort();
    //     b.sort();
    //     return JSON.stringify(a) === JSON.stringify(b)
    // };

    /**
     Search for similar items in both arrays.
     */
    const equalItems = (categories, acceptedValues) => {
        if (categories.length > acceptedValues.length) {
            return false;
        }

        let similarSlice = [];
        categories.forEach((category) => {
            if (acceptedValues.indexOf(category) >= 0) {
                similarSlice.push(category);
            }
        })

        return similarSlice.length === categories.length;
    }

    /**
     * Filter institutions by provided categories.
     */
    FirstFormNextButton.addEventListener('click', () => {
        const institutions = document.querySelectorAll("div[data-step='3'] div.form-group--checkbox");

        let countDisabledChunks = 0;
        institutions.forEach((institution) => {
            institution.addEventListener('change', evt => {
                if (ThirdFormNextButton.style.display == "none") {
                    ThirdFormNextButton.style.display ="block"
                }
            })

            const institutionValues = institution.querySelector('input[name=accepted_values]').value;
            let values = [];
            [...institutionValues].forEach((number) => {
                if (Number(number)) {
                    values.push(Number(number))
                }
            });

            if (!equalItems(categoriesId, values)) {
                institution.style.display = "none";
                countDisabledChunks++;
            }

            if (institutions.length === countDisabledChunks) {
                ThirdFormNextButton.style.display = "none";
            }

        })
        SecondFormPrevButton.addEventListener('click', () => {
            ThirdFormNextButton.style.display = "block";

            institutions.forEach((institution) => {
                institution.style.display = "block";
            });
        });
    });

    /**
     *
     */
    const FourthFormNextButton = document.querySelector("div[data-step='4'] button.next-step");

    FourthFormNextButton.addEventListener('click', () => {
        const userProvidedInformation = [];
        document.querySelectorAll("div[data-step='4'] input").forEach((input) => {
            userProvidedInformation.push(input.value);
        })

        /**
         * User Info.
         */

        const bagsQuantity = document.querySelector("div[data-step='2'] input").value;
        let institutionName = null;
        const institutions = document.querySelectorAll("div[data-step='3'] input[name=organization]");
        institutions.forEach((institution) => {
            if (institution.checked) {
                institutionName = institution.parentElement.querySelector("div.title").innerText;
            }
        })

        let userInformation = [street, city, zipCode, phone, date, hour] = userProvidedInformation;
        let remarks = document.querySelector("div[data-step='4'] textarea").value;
        if (!remarks) {
            remarks = 'Brak uwag';
        }
        userInformation.push(remarks);


        /**
         * Update summary.
         */

        let summaryHeader = document.querySelectorAll("div[data-step='5'] span.summary--text");
        summaryHeader[0].innerText = `${bagsQuantity} worki ${categoriesNames}`;
        summaryHeader[1].innerText = institutionName;

        let summaryContent = document.querySelectorAll("div[data-step='5'] div.form-section--column");

        const address = summaryContent[0].querySelectorAll('li');
        for (let i = 0; i < address.length; i++) {
            address[i].innerText = userInformation[i];
        }

        const parcelPickUpTime = summaryContent[1].querySelectorAll('li');
        for (let i = 0; i < parcelPickUpTime.length; i++) {
            parcelPickUpTime[i].innerText = userInformation[address.length + i];
        }
    });
});