// content.js

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fillForm") {
        fillForm(sendResponse);
        // Indicate that the response will be sent asynchronously
        return true;
    }
});

/**
 * Extracts form fields, sends them to the backend, and fills the form with responses.
 * @param {Function} sendResponse - The callback to send the response back to popup.
 */
async function fillForm(sendResponse) {
    try {
        // Extract all forms on the page
        const forms = document.querySelectorAll('form');
        if (forms.length === 0) {
            sendResponse({ status: "No forms found on this page." });
            return;
        }

        
        // For simplicity, we'll process the first form found
        const form = forms[0];
        const inputs = form.querySelectorAll('input, textarea, select');
        let formFields = [];

        // Initialize a map to store hidden labels by input name
        const hiddenLabelsMap = {};
        // Initialize a map to store references to visible inputs by name
        const visibleInputsMap = {};


        inputs.forEach(input => {
            const name = input.name || input.id || input.placeholder;
            const type = input.type.toLowerCase();
            if(!name){// Skip inputs without a name, id, or placeholder
                return
            }
            const label = getLabel(input);

            // // Checking through printing out the response
            // if (name === 'cards[9634bbda-1eee-4b72-a6dc-32689024e8fe][field0]' ){
            //     console.log(`Name: '${name}', Label: '${label}'`);
            // }
            
            
            // Check if the input is of type 'hidden'
            if (type === 'hidden' || type === '') {
                if (label) {
                    hiddenLabelsMap[name] = label;
                    
                    // If a visible input with the same name was processed earlier, update its label (Chalta he ni yeh loop)
                    if (visibleInputsMap[name]) {
                        visibleInputsMap[name].label += ' ' + label;
                        console.log(`[Update] Appended hidden label to visible input with Name: ${name}`);
                    }
                }
            }            
            else {
                let comprehensiveLabel = label;

                try{
                    const optionLabel = getOptionLabel(input);
                    if (optionLabel) {
                        comprehensiveLabel += ' ' + optionLabel;
                    }
                }
                catch (error) {
                    console.error('Error filling Optinal Label:', error);
                }
                
                if (hiddenLabelsMap[name]) {
                    // Append the hidden labels to the current label, separated by a space
                    comprehensiveLabel += ' ' + hiddenLabelsMap[name];
                }

                const field = {
                    name: name,
                    label: comprehensiveLabel.replace(/\*/g, ''), // Trim to remove any extra spaces
                    type: input.type, // Capture the input type
                };
                
                formFields.push(field);

                // Store a reference to this field in case a hidden input appears later
                visibleInputsMap[name] = field;
            }
        });
                

        // Prepare data to send to the Flask backend
        const data = {
            formFields: formFields
        };

        // Send data to the Flask backend
        const response = await fetch('http://localhost:5000/fill-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            sendResponse({ status: `Backend error: ${response.statusText}` });
            return;
        }

        const result = await response.json();
        const filledFields = result.filledFields;

        // Fetch the resume file from the backend
        const resumeResponse = await fetch('http://localhost:5000/resume', {
            headers: {
                // Include any necessary headers, e.g., Authorization
            }
        });
        if (!resumeResponse.ok) {
            sendResponse({ status: `Resume fetch error: ${resumeResponse.statusText}` });
            return;
        }
        const resumeBlob = await resumeResponse.blob();
        const resumeFile = new File([resumeBlob], "resume.pdf", { type: "application/pdf" });


        // Fetch the transcript file from the backend
        const transcriptResponse = await fetch('http://localhost:5000/transcript', {
            headers: {
                // Include any necessary headers, e.g., Authorization
            }
        });
        if (!transcriptResponse.ok) {
            sendResponse({ status: `Transcript fetch error: ${transcriptResponse.statusText}` });
            return;
        }
        const transcriptBlob = await transcriptResponse.blob();
        const transcriptFile = new File([transcriptBlob], "transcript.pdf", { type: "application/pdf" });


        // Function to simulate user clicks
        function simulateClick(element) {
            const event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            element.dispatchEvent(event);
        }


        // Handling the resume anomaly
        const form_anomaly = document.getElementById("s3_upload_for_resume");
        if(form_anomaly){
            const fileInput = form_anomaly.querySelector("input[type='file']");
            if (fileInput){
                uploadFile(fileInput, resumeFile);
                console.log("Uploaded the resume");
            }
        }
        

        // Fill the form fields with the returned data
        filledFields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"], [id="${field.name}"]`);
            if (input) {
                if (input.type === 'file') {
                    // Handle file input (e.g., resume upload)
                    console.log(`file label'${getLabel(input).toLowerCase()}'`)
                    if (getLabel(input).toLowerCase().includes('resume') || getLabel(input).toLowerCase().includes('cv')){
                        console.log("Resume addresed");
                        uploadFile(input, resumeFile);                       
                    }
                    else if(getLabel(input).toLowerCase().includes('transcript')){
                        console.log("Transcript addresed");
                        uploadFile(input, transcriptFile);                        
                    }
 
                } else if (input.tagName.toLowerCase() === 'select') {
                    // Improved select handling
                    handleSelectField(input, field.value);
                } else if (input.type.includes('check')) {
                    if (field.value.toLowerCase() === 'true'){
                        simulateClick(input);
                    }
                    // input.checked = field.value.toLowerCase() === 'true';
                    // simulateClick(input);
                } else if (input.type.includes('radio')) {
                    if (field.value.toLowerCase() === 'true') {
                        input.checked = true;
                        simulateClick(input);
                        // input.dispatchEvent(new Event('change', { bubbles: !0, cancelable: !1 }));
                    }
                } else if (input.type.includes('button')) {
                    if (field.value.toLowerCase() === 'true') {
                        simulateClick(input);
                        // input.dispatchEvent(new Event('change', { bubbles: !0, cancelable: !1 }));
                    }
                } else {
                    input.value = field.value;
                    // Dispatch input events to ensure any JS listeners are triggered
                    input.dispatchEvent(new Event('input', { bubbles: !0, cancelable: !1}));
                }
            }
        });

        // asdasdasdasd

        const submitButton = document.getElementById('btn-submit');
        if (submitButton) {
            // Optionally, ensure the button is not disabled and is visible
            if (!submitButton.disabled && submitButton.offsetParent !== null) {
                await delay(2000);
                simulateClick(submitButton);
                console.log("Submit button clicked.");
            } else {
                console.warn("Submit button is either disabled or not visible.");
            }
        } else {
            console.warn("Submit button with ID 'btn-submit' not found.");
        }

        // asdasdasd

        sendResponse({ status: "Form filled successfully." });
    } catch (error) {
        console.error('Error filling form:', error);
        sendResponse({ status: "Error filling form." });
    }
}

/**
 * Retrieves the label text associated with an input element.
 * @param {HTMLElement} input - The input element.
 * @returns {string} - The label text.
 */
function getLabel(input) {
    let labelParts = [];

    // 1. Extract higher-level label from ancestor <h4> elements
    const section = input.closest('div.section.page-centered.application-form');
    if (section) {
        const h4 = section.querySelector('h4[data-qa="card-name"]');
        if (h4) {
            const h4Text = h4.innerText.trim();
            if (h4Text) {
                labelParts.push(h4Text);
            }
        }
    }

    // 2. Extract the immediate label within the closest <li>
    const li = input.closest('li.application-question, li.custom-question');
    if (li) {
        const labelElement = li.querySelector('.application-label .text, .custom-label .text, .application-label, .custom-label');
        try{
            if (labelElement) {
                // Clone the label element to remove child elements like <span class="required">
                const clonedLabel = labelElement.cloneNode(true);
                const spans = clonedLabel.querySelectorAll('span');
                spans.forEach(span => clonedLabel.removeChild(span));
    
                const immediateLabel = clonedLabel.innerText.trim();
                if (immediateLabel) {
                    labelParts.push(immediateLabel);
                }
            }
        }
        catch (error) {
            console.error('Error filling form:', error);
        }
    }

    // 3. Extract the option label if it's a grouped input (radio, checkbox)
    let optionLabel = '';
    if (['radio', 'checkbox'].includes(input.type.toLowerCase())) {
        optionLabel = getOptionLabel(input);
        if (optionLabel) {
            labelParts.push(optionLabel);
        }
    }

    // 4. Combine all label parts into a single string
    const combinedLabel = labelParts.join(' ').replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();

    // 5. Fallback to other methods if labels are still missing
    if (!combinedLabel) {
        // Check associated <label> elements
        if (input.labels && input.labels.length > 0) {
            const associatedLabel = input.labels[0].innerText.trim();
            if (associatedLabel) {
                return associatedLabel;
            }
        }

        // Check for placeholder
        if (input.placeholder) {
            return input.placeholder.trim();
        }
    }

    return combinedLabel;
}

/**
 * Returns a Promise that resolves after the specified milliseconds.
 * @param {number} ms - The number of milliseconds to wait.
 * @returns {Promise} - A Promise that resolves after `ms` milliseconds.
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retrieves the label text for an option input (e.g., radio, checkbox).
 * @param {HTMLElement} input - The input element.
 * @returns {string} - The option label text.
 */
function getOptionLabel(input) {
    let optionLabel = '';

    // Attempt to find the sibling element that contains the label text
    // This assumes the structure: <label><input ...><span>Label Text</span></label>
    const parentLabel = input.closest('label');
    if (parentLabel) {
        const span = parentLabel.querySelector('span, .application-answer-alternative');
        if (span) {
            optionLabel = span.innerText.trim();
            return optionLabel;
        }

        // If no span, get the remaining text
        const clonedLabel = parentLabel.cloneNode(true);
        clonedLabel.removeChild(input); // Remove the input element
        optionLabel = clonedLabel.innerText.trim();
        return optionLabel;
    }

    // Fallback to placeholder or value
    if (input.placeholder) {
        optionLabel = input.placeholder.trim();
    } else if (input.value) {
        optionLabel = input.value.trim();
    }

    return optionLabel;
}



/**
 * Uploads a file to a file input field.
 * @param {HTMLElement} field - The file input field.
 * @param {File} file - The file to upload.
 */
function uploadFile(field, file) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    field.files = dataTransfer.files;
    console.log(`[MyExtension] Uploaded file '${file.name}' to '${field.name}'`);

    // Dispatch change event to notify any listeners
    const event = new Event('change', { bubbles: true });
    field.dispatchEvent(event);
}

/**
 * Handles the selection of options in a select field.
 * @param {HTMLSelectElement} selectField - The select element.
 * @param {string} value - The value to select.
 */
function handleSelectField(selectField, value) {
    const options = Array.from(selectField.options);
    const lowerValue = value.toLowerCase();

    // Attempt exact match first
    let optionToSelect = options.find(option => option.value.toLowerCase() === lowerValue);

    // If no exact match, attempt partial match
    if (!optionToSelect) {
        optionToSelect = options.find(option => option.value.toLowerCase().includes(lowerValue) || option.text.toLowerCase().includes(lowerValue));
    }

    // If still no match, default to the first option or leave as is
    if (optionToSelect) {
        selectField.value = optionToSelect.value;
        // Dispatch change event
        selectField.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        console.warn(`No matching option found for select field with value: ${value}`);
    }
}
