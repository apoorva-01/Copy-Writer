class CopywritingAgent {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadBrands();
        this.uploadedImage = null;
        this.analyzedSections = null;
        this.uploadedImageName = null;
    }

    initializeElements() {
        // Upload elements
        this.imageUploadArea = document.getElementById('imageUploadArea');
        this.docsUploadArea = document.getElementById('docsUploadArea');
        this.imageUpload = document.getElementById('imageUpload');
        this.docsUpload = document.getElementById('docsUpload');
        this.docsUrlInput = document.getElementById('docsUrlInput');
        this.docsPreview = document.getElementById('docsPreview');
        this.previewImage = document.getElementById('previewImage');
        
        // Brand elements
        this.brandSelect = document.getElementById('brandSelect');
        this.customBrandInput = document.getElementById('customBrandInput');
        this.existingBrandContainer = document.getElementById('existingBrandContainer');
        this.customBrandContainer = document.getElementById('customBrandContainer');
        
        // Radio buttons
        this.existingBrandRadio = document.getElementById('existingBrandRadio');
        this.customBrandRadio = document.getElementById('customBrandRadio');
        this.imageUploadRadio = document.getElementById('imageUploadRadio');
        this.docsUploadRadio = document.getElementById('docsUploadRadio');
        
        // Other elements
        this.additionalContext = document.getElementById('additionalContext');
        this.form = document.getElementById('copywritingForm');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingState = document.getElementById('loadingState');
        this.confirmationSection = document.getElementById('confirmationSection');
        this.confirmationContent = document.getElementById('confirmationContent');
        this.editAnalysisBtn = document.getElementById('editAnalysisBtn');
        this.confirmAnalysisBtn = document.getElementById('confirmAnalysisBtn');
        this.addSectionBtn = document.getElementById('addSectionBtn');
        this.addSectionModal = document.getElementById('addSectionModal');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContent = document.getElementById('resultsContent');
        this.errorDisplay = document.getElementById('errorDisplay');
        this.sheetLink = document.getElementById('sheetLink');
    }

    attachEventListeners() {
        // Brand type radio buttons
        this.existingBrandRadio.addEventListener('change', () => this.handleBrandTypeChange());
        this.customBrandRadio.addEventListener('change', () => this.handleBrandTypeChange());
        
        // Upload type radio buttons
        this.imageUploadRadio.addEventListener('change', () => this.handleUploadTypeChange());
        this.docsUploadRadio.addEventListener('change', () => this.handleUploadTypeChange());
        
        // Image upload events
        this.imageUploadArea.addEventListener('click', () => this.imageUpload.click());
        this.imageUploadArea.addEventListener('dragover', (e) => this.handleDragOver(e, 'image'));
        this.imageUploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e, 'image'));
        this.imageUploadArea.addEventListener('drop', (e) => this.handleDrop(e, 'image'));
        this.imageUpload.addEventListener('change', (e) => this.handleFileSelect(e, 'image'));

        // Docs upload events
        this.docsUploadArea.addEventListener('click', () => this.docsUpload.click());
        this.docsUploadArea.addEventListener('dragover', (e) => this.handleDragOver(e, 'docs'));
        this.docsUploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e, 'docs'));
        this.docsUploadArea.addEventListener('drop', (e) => this.handleDrop(e, 'docs'));
        this.docsUpload.addEventListener('change', (e) => this.handleFileSelect(e, 'docs'));
        
        // Docs URL input
        this.docsUrlInput.addEventListener('input', (e) => this.handleDocsUrlInput(e));
        this.docsUrlInput.addEventListener('paste', (e) => this.handleDocsUrlPaste(e));

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Confirmation buttons
        this.editAnalysisBtn.addEventListener('click', () => this.enableEditing());
        this.confirmAnalysisBtn.addEventListener('click', () => this.proceedWithCopyGeneration());
        this.addSectionBtn.addEventListener('click', () => this.showAddSectionModal());
    }

    handleBrandTypeChange() {
        if (this.existingBrandRadio.checked) {
            this.existingBrandContainer.style.display = 'block';
            this.customBrandContainer.style.display = 'none';
            this.brandSelect.required = true;
            this.customBrandInput.required = false;
        } else {
            this.existingBrandContainer.style.display = 'none';
            this.customBrandContainer.style.display = 'block';
            this.brandSelect.required = false;
            this.customBrandInput.required = true;
        }
    }

    handleUploadTypeChange() {
        if (this.imageUploadRadio.checked) {
            this.imageUploadArea.style.display = 'flex';
            this.docsUploadArea.style.display = 'none';
            // Update generate button text
            this.generateBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Design';
        } else {
            this.imageUploadArea.style.display = 'none';
            this.docsUploadArea.style.display = 'flex';
            // Update generate button text
            this.generateBtn.innerHTML = '<i class="fas fa-file-text"></i> Process Document';
        }
    }

    handleDragOver(e, type) {
        e.preventDefault();
        const uploadArea = type === 'image' ? this.imageUploadArea : this.docsUploadArea;
        uploadArea.classList.add('dragover');
    }

    handleDragLeave(e, type) {
        e.preventDefault();
        const uploadArea = type === 'image' ? this.imageUploadArea : this.docsUploadArea;
        uploadArea.classList.remove('dragover');
    }

    handleDrop(e, type) {
        e.preventDefault();
        const uploadArea = type === 'image' ? this.imageUploadArea : this.docsUploadArea;
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0], type);
        }
    }

    handleFileSelect(e, type) {
        const files = e.target.files;
        if (files.length > 0) {
            this.handleFile(files[0], type);
        }
    }

    handleDocsUrlInput(e) {
        const url = e.target.value.trim();
        if (url && this.isValidGoogleDocsUrl(url)) {
            this.processGoogleDocsUrl(url);
        }
    }

    handleDocsUrlPaste(e) {
        setTimeout(() => {
            const url = e.target.value.trim();
            if (url && this.isValidGoogleDocsUrl(url)) {
                this.processGoogleDocsUrl(url);
            }
        }, 100);
    }

    isValidGoogleDocsUrl(url) {
        return url.includes('docs.google.com/document/') || url.includes('drive.google.com/file/');
    }

    handleFile(file, type = 'image') {
        if (type === 'image') {
            this.handleImageFile(file);
        } else {
            this.handleDocsFile(file);
        }
    }

    handleImageFile(file) {
        if (!file.type.startsWith('image/')) {
            this.showError('Please select an image file (PNG, JPG, WEBP)');
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            this.showError('File size must be less than 16MB');
            return;
        }

        this.uploadedImage = file;
        this.uploadedImageName = file.name;
        this.uploadedDocs = null; // Clear docs data
        
        // Hide upload icon and features
        const uploadIcon = this.imageUploadArea.querySelector('.upload-icon');
        const uploadFeatures = this.imageUploadArea.querySelector('.upload-features');
        if (uploadIcon) uploadIcon.style.display = 'none';
        if (uploadFeatures) uploadFeatures.style.display = 'none';
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewImage.style.display = 'block';
            
            // Update upload area
            this.imageUploadArea.querySelector('.upload-text').textContent = file.name;
            this.imageUploadArea.querySelector('.upload-subtext').textContent = 'Click to change image';
        };
        reader.readAsDataURL(file);

        this.hideError();
    }

    handleDocsFile(file) {
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/pdf',
            'text/plain'
        ];

        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(docx|doc|pdf|txt)$/i)) {
            this.showError('Please select a document file (DOCX, DOC, PDF, TXT)');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            this.showError('Document size must be less than 10MB');
            return;
        }

        this.uploadedDocs = file;
        this.uploadedImage = null; // Clear image data
        
        // Hide upload icon and features
        const uploadIcon = this.docsUploadArea.querySelector('.upload-icon');
        const uploadFeatures = this.docsUploadArea.querySelector('.upload-features');
        if (uploadIcon) uploadIcon.style.display = 'none';
        if (uploadFeatures) uploadFeatures.style.display = 'none';
        
        // Show preview
        this.docsPreview.style.display = 'block';
        this.docsPreview.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-file-alt" style="color: var(--brand-primary);"></i>
                <strong>${file.name}</strong>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.85rem;">
                Document uploaded successfully. Click "Process Document" to extract and analyze content.
            </div>
        `;
        
        // Update upload area
        this.docsUploadArea.querySelector('.upload-text').textContent = file.name;
        this.docsUploadArea.querySelector('.upload-subtext').textContent = 'Click to change document';

        this.hideError();
    }

    processGoogleDocsUrl(url) {
        this.uploadedDocsUrl = url;
        this.uploadedImage = null; // Clear image data
        this.uploadedDocs = null; // Clear file data
        
        // Hide upload icon and features
        const uploadIcon = this.docsUploadArea.querySelector('.upload-icon');
        const uploadFeatures = this.docsUploadArea.querySelector('.upload-features');
        if (uploadIcon) uploadIcon.style.display = 'none';
        if (uploadFeatures) uploadFeatures.style.display = 'none';
        
        // Show preview
        this.docsPreview.style.display = 'block';
        this.docsPreview.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-link" style="color: var(--brand-primary);"></i>
                <strong>Google Docs URL</strong>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.85rem; word-break: break-all;">
                ${url}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.5rem;">
                URL detected. Click "Process Document" to extract and analyze content.
            </div>
        `;
        
        // Update upload area
        this.docsUploadArea.querySelector('.upload-text').textContent = 'Google Docs URL added';
        this.docsUploadArea.querySelector('.upload-subtext').textContent = 'Ready to process';

        this.hideError();
    }

    async loadBrands() {
        try {
            const response = await fetch('/api/brands');
            const data = await response.json();
            
            if (data.brands) {
                this.brandSelect.innerHTML = '<option value="">Choose a brand...</option>';
                data.brands.forEach(brand => {
                    const option = document.createElement('option');
                    option.value = brand;
                    option.textContent = brand;
                    this.brandSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading brands:', error);
            this.showError('Failed to load brands. Please refresh the page.');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        // Validate input based on type
        const isImageMode = this.imageUploadRadio.checked;
        
        if (isImageMode) {
            if (!this.uploadedImage) {
                this.showError('Please upload an image first.');
                return;
            }
        } else {
            if (!this.uploadedDocs && !this.uploadedDocsUrl) {
                this.showError('Please upload a document or provide a Google Docs URL.');
                return;
            }
        }

        // Validate brand selection
        const brandName = this.getBrandName();
        if (!brandName) {
            if (this.existingBrandRadio.checked) {
                this.showError('Please select a brand.');
            } else {
                this.showError('Please enter a custom client name.');
            }
            return;
        }

        this.setLoading(true, isImageMode ? 'Analyzing your design...' : 'Processing your document...', true);
        this.hideError();
        this.hideResults();
        this.hideConfirmation();

        try {
            if (isImageMode) {
                // Step 1: Analyze the image (show progress)
                this.updateProgressStep(1, 'active');
                const sections = await this.analyzeImage();
                this.updateProgressStep(1, 'completed');
                this.analyzedSections = sections;
                
                // Step 2: Show confirmation (don't generate copy yet)
                this.showAnalysisConfirmation(sections);
            } else {
                // Process document mode
                await this.processDocument();
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message || 'An error occurred while processing. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    getBrandName() {
        if (this.existingBrandRadio.checked) {
            return this.brandSelect.value.trim();
        } else {
            return this.customBrandInput.value.trim();
        }
    }

    async analyzeImage() {
        const formData = new FormData();
        formData.append('image', this.uploadedImage);

        const response = await fetch('/api/analyze-image', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to analyze image');
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to analyze image');
        }

        // Store image path for later use in copy generation
        this.imagePath = data.image_path;
        return data.sections;
    }

    async generateCopyWithProgress(sections) {
        // Step 1: Analyzing design structure (already completed during image analysis)
        this.updateProgressStep(1, 'completed');

        // Step 2: Understanding brand context (fetch Google Docs data)
        this.updateProgressStep(2, 'active');
        
        try {
            await this.generateCopyWithDetailedProgress(sections);
        } catch (error) {
            throw error; // Re-throw to be handled by the calling method
        }
    }

    async generateCopyWithDetailedProgress(sections) {
        // Get the updated context from the confirmation screen
        const confirmationContextEl = document.getElementById('confirmationContext');
        const additionalContext = confirmationContextEl ? confirmationContextEl.value : this.additionalContext.value;

        const payload = {
            sections: sections,
            brand_name: this.getBrandName(), // Use getBrandName() for consistency
            additional_context: additionalContext,
            image_path: this.imagePath || ''
        };

        // Mark brand context as completed when we start the request (backend will fetch Google Docs)
        this.updateProgressStep(2, 'completed');
        
        // Steps 3 & 4: Both OpenAI calls happen during this single request
        this.updateProgressStep(3, 'active');
        
        const response = await fetch('/api/generate-copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            // Try to get detailed error message from response
            let errorMessage = 'Failed to generate copy';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If JSON parsing fails, use default message
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to generate copy');
        }

        // Show visual progression of the two OpenAI operations
        this.updateProgressStep(3, 'completed');
        this.updateProgressStep(4, 'active');
        await this.delay(300); // Brief pause to show progression
        this.updateProgressStep(4, 'completed');

        // Step 5: Finalizing results
        this.updateProgressStep(5, 'active');
        this.displayResults(data);
        await this.delay(200); // Brief delay for visual feedback
        this.updateProgressStep(5, 'completed');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async generateCopy(sections) {
        // Get the updated context from the confirmation screen
        const confirmationContextEl = document.getElementById('confirmationContext');
        const additionalContext = confirmationContextEl ? confirmationContextEl.value : this.additionalContext.value;

        const payload = {
            sections: sections,
            brand_name: this.getBrandName(), // Use getBrandName() for both existing and custom brands
            additional_context: additionalContext,
            image_path: this.imagePath || '' // Send image path for new pipeline
        };

        // Mark brand context as completed when we start the request (backend will fetch Google Docs)
        this.updateProgressStep(2, 'completed');

        const response = await fetch('/api/generate-copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to generate copy');
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to generate copy');
        }

        this.displayResults(data);
    }

    displayResults(data) {
        console.log('🎯 Displaying results:', data);
        this.resultsContent.innerHTML = '';

        // NEW PIPELINE (Image) OR DOCUMENT PIPELINE: Display structured data + final HTML
        if ((data.pipeline_version === 'new' || data.pipeline_version === 'document') && data.final_html) {
            console.log('📄 Using new/document pipeline display');
            this.displayNewPipelineResults(data);
        } 
        // LEGACY PIPELINE: Display section-by-section results
        else if (data.results) {
            console.log('📜 Using legacy pipeline display');
            this.displayLegacyResults(data);
        }
        else {
            console.log('⚠️ Unknown result format:', data);
            // Fallback display
            this.resultsContent.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: #666;">
                    <h3>Processing Complete</h3>
                    <p>Results received but display format not recognized.</p>
                    <pre style="text-align: left; max-height: 200px; overflow-y: auto; background: #f5f5f5; padding: 1rem; border-radius: 8px;">${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
        }
        
        this.showResults();
    }

    displayNewPipelineResults(data) {
        const { section_copy_data, final_html } = data;
        console.log('🎨 Rendering results with:', { 
            hasHTML: !!final_html, 
            hasCopyData: !!section_copy_data,
            pipelineVersion: data.pipeline_version 
        });

        // For document pipeline, show product info summary
        if (data.pipeline_version === 'document' && section_copy_data) {
            const productSummaryDiv = document.createElement('div');
            productSummaryDiv.className = 'improvement-ideas';
            
            if (section_copy_data.multiple_products) {
                // Multiple products summary
                productSummaryDiv.innerHTML = `
                    <div class="ideas-section">
                        <h4><i class="fas fa-shopping-cart"></i> Multi-Product Analysis Summary</h4>
                        <div class="ideas-content">
                            <p><strong>Products Processed:</strong> ${section_copy_data.product_count} products found and processed</p>
                            <p><strong>Products:</strong></p>
                            <ul style="margin-left: 1rem; margin-top: 0.5rem;">
                                ${section_copy_data.products.map(product => 
                                    `<li><strong>${product.product_name}</strong> - ${product.key_value_proposition || 'Premium solution'}</li>`
                                ).join('')}
                            </ul>
                            <p style="margin-top: 1rem;"><em>✨ Generated individual marketing copy for each product with tailored messaging and CTAs</em></p>
                        </div>
                    </div>
                `;
            } else if (section_copy_data.product_name) {
                // Single product summary
                productSummaryDiv.innerHTML = `
                    <div class="ideas-section">
                        <h4><i class="fas fa-bullseye"></i> Product Analysis Summary</h4>
                        <div class="ideas-content">
                            <p><strong>Product:</strong> ${section_copy_data.product_name}</p>
                            <p><strong>Value Proposition:</strong> ${section_copy_data.key_value_proposition || 'N/A'}</p>
                            <p><strong>Target Audience:</strong> ${section_copy_data.target_audience || 'N/A'}</p>
                            ${section_copy_data.primary_benefits ? `<p><strong>Key Benefits:</strong> ${section_copy_data.primary_benefits.join(', ')}</p>` : ''}
                        </div>
                    </div>
                `;
            }
            
            this.resultsContent.appendChild(productSummaryDiv);
        }

        // Display improvement ideas if available (for image pipeline)
        if (section_copy_data && section_copy_data.ideas) {
            const ideasDiv = document.createElement('div');
            ideasDiv.className = 'improvement-ideas';
            ideasDiv.innerHTML = `
                <div class="ideas-section">
                    <h4><i class="fas fa-lightbulb"></i> Strategic Improvement Insights</h4>
                    <div class="ideas-content">
                        <p>${section_copy_data.ideas}</p>
                    </div>
                </div>
            `;
            this.resultsContent.appendChild(ideasDiv);
        }

        // Display structured data summary
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'pipeline-summary';
        summaryDiv.innerHTML = `
          
        `;
        this.resultsContent.appendChild(summaryDiv);

        // Display section copy data
        // if (section_copy_data && section_copy_data.sections) {
        //     const dataDiv = document.createElement('div');
        //     dataDiv.className = 'section-copy-display';
        //     let sectionsHtml = '';
            
        //     section_copy_data.sections.forEach((section, index) => {
        //         let copyOptionsHtml = '';
                
        //         if (section.copy_options && section.copy_options.length > 0) {
        //             // NEW FORMAT: Multiple copy options with confidence scores
        //             copyOptionsHtml = `<div class="copy-options">`;
        //             section.copy_options.forEach((option, optionIndex) => {
        //                 const confidenceClass = option.confidence >= 90 ? 'high-confidence' : 
        //                                       option.confidence >= 80 ? 'medium-confidence' : 'low-confidence';
        //                 copyOptionsHtml += `
        //                     <div class="copy-option ${confidenceClass}">
        //                         <div class="option-header">
        //                             <span class="option-number">Option ${optionIndex + 1}</span>
        //                             <span class="confidence-score">${option.confidence}% confidence</span>
        //                         </div>
        //                         <div class="option-text">${this.formatCopyText(option.generated_text)}</div>
        //                         <div class="option-justification">
        //                             <strong>Why this converts:</strong> ${option.justification}
        //                         </div>
        //                     </div>
        //                 `;
        //             });
        //             copyOptionsHtml += `</div>`;
        //         } else if (section.generated_text) {
        //             // LEGACY FORMAT: Single generated text
        //             copyOptionsHtml = `
        //                 <div class="generated-copy">${this.formatCopyText(section.generated_text)}</div>
        //             `;
        //         }
                
        //         sectionsHtml += `
        //             <div class="section-copy-item">
        //                 <h5><strong>${section.section_name || `Section ${index + 1}`}</strong></h5>
        //                 <p><strong>Purpose:</strong> ${section.communicates || 'N/A'}</p>
        //                 <p><strong>Structure:</strong> ${section.text_structure || 'N/A'}</p>
        //                 <div class="copy-content">
        //                     ${copyOptionsHtml}
        //                 </div>
        //             </div>
        //         `;
        //     });
            
        //     dataDiv.innerHTML = `
        //         <div class="data-section">
        //             <h4><i class="fas fa-edit"></i> Generated Section Copy</h4>
        //             <div class="data-content">
        //                 ${sectionsHtml}
        //             </div>
        //         </div>
        //     `;
        //     this.resultsContent.appendChild(dataDiv);
        // }

        // Display final HTML
        const htmlDiv = document.createElement('div');
        htmlDiv.className = 'final-html-display';
        htmlDiv.innerHTML = `
            <div class="html-section">
                <div class="html-controls">
                    <button class="preview-btn" data-action="preview">
                        <i class="fas fa-external-link-alt"></i> Open in New Tab
                    </button>
                    <button class="copy-html-btn" data-action="copy">
                        <i class="fas fa-copy"></i> Copy HTML
                    </button>
                    <button class="toggle-code-btn" data-action="toggle">
                        <i class="fas fa-code"></i> Show Code
                    </button>
                </div>
                <div class="html-preview" style="display: block;">
                    <div class="iframe-loading" style="display: none;">
                        <div class="loading-spinner"></div>
                        <p>Loading preview...</p>
                    </div>
                    <iframe class="html-iframe" style="opacity: 0;"></iframe>
                </div>
                <div class="html-code" style="display: none;">
                    <pre><code>${this.escapeHtml(final_html)}</code></pre>
                </div>
            </div>
        `;
        this.resultsContent.appendChild(htmlDiv);

        // Set iframe content using srcdoc and handle loading
        const iframe = htmlDiv.querySelector('.html-iframe');
        const loadingDiv = htmlDiv.querySelector('.iframe-loading');
        
        if (iframe && loadingDiv) {
            // Show loading state
            loadingDiv.style.display = 'block';
            iframe.style.opacity = '0';
            
            // Set iframe content
            iframe.srcdoc = final_html;
            
            // Handle iframe load with multiple fallbacks
            let loaded = false;
            
            iframe.onload = () => {
                if (!loaded) {
                    loaded = true;
                    loadingDiv.style.display = 'none';
                    iframe.style.opacity = '1';
                }
            };
            
            // Fallback timeout
            setTimeout(() => {
                if (!loaded) {
                    loaded = true;
                    loadingDiv.style.display = 'none';
                    iframe.style.opacity = '1';
                }
            }, 1000);
        }

        // Add event listeners for HTML control buttons
        const previewBtn = htmlDiv.querySelector('.preview-btn');
        const copyBtn = htmlDiv.querySelector('.copy-html-btn');
        const toggleBtn = htmlDiv.querySelector('.toggle-code-btn');
        const htmlPreview = htmlDiv.querySelector('.html-preview');
        const htmlCode = htmlDiv.querySelector('.html-code');
        
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewHTML(encodeURIComponent(final_html));
            });
        }
        
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyToClipboard(encodeURIComponent(final_html));
            });
        }

        // Ensure preview is shown by default
        htmlPreview.style.display = 'block';
        htmlCode.style.display = 'none';
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const isCodeVisible = htmlCode.style.display !== 'none';
                if (isCodeVisible) {
                    htmlCode.style.display = 'none';
                    htmlPreview.style.display = 'block';
                    toggleBtn.innerHTML = '<i class="fas fa-code"></i> Show Code';
                } else {
                    htmlCode.style.display = 'block';
                    htmlPreview.style.display = 'none';
                    toggleBtn.innerHTML = '<i class="fas fa-globe"></i> Show Preview';
                }
            });
        }

        // Display compact copy options summary below HTML preview
        this.displayCopyOptionsCompact(section_copy_data);
    }

    displayLegacyResults(data) {
        const { results, sheet_url } = data;

        results.forEach(result => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section-result';
            
            sectionDiv.innerHTML = `
                <div class="section-header">
                    <div class="section-title">${result.section_id.replace('_', ' ').toUpperCase()}</div>
                    <div class="section-type">${result.section_type}</div>
                </div>
                <div class="copy-versions">
                    <div class="copy-version final">
                        <h4><i class="fas fa-star"></i> Final Copy</h4>
                        <div class="copy-text">${this.formatCopyText(result.final_copy)}</div>
                    </div>
                </div>
            `;
            
            this.resultsContent.appendChild(sectionDiv);
        });

        // Show sheet link if available
        if (sheet_url && sheet_url !== "https://sheets.google.com/mock-sheet-url") {
            this.sheetLink.style.display = 'block';
            this.sheetLink.querySelector('a').href = sheet_url;
        }

        this.showResults();
    }

    formatCopyText(text) {
        if (!text || text.trim() === '') {
            return '<p>No content available</p>';
        }
        
        // Clean up the text first
        const cleanText = text.trim();
        
        // Split by double line breaks to create paragraphs
        const paragraphs = cleanText.split(/\n\s*\n/);
        
        // Process each paragraph
        const formattedParagraphs = paragraphs
            .filter(p => p.trim()) // Remove empty paragraphs
            .map(paragraph => {
                // Replace single line breaks within paragraphs with <br>
                const formattedParagraph = paragraph.trim().replace(/\n/g, '<br>');
                return `<p>${formattedParagraph}</p>`;
            });
        
        return formattedParagraphs.join('');
    }

    // Utility methods for new pipeline
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatGeneratedText(text) {
        // Handle if text is an object (structured text with multiple fields)
        if (typeof text === 'object' && text !== null) {
            let formatted = '';
            
            // Handle common structured text patterns
            if (text.headline) {
                formatted += `<strong>Headline:</strong> ${text.headline}<br>`;
            }
            if (text.section_title) {
                formatted += `<strong>Title:</strong> ${text.section_title}<br>`;
            }
            if (text.promotional_text) {
                formatted += `<strong>Text:</strong> ${text.promotional_text}<br>`;
            }
            if (text.email_input_placeholder) {
                formatted += `<strong>Email placeholder:</strong> ${text.email_input_placeholder}<br>`;
            }
            if (text.submit_button_text) {
                formatted += `<strong>Button:</strong> ${text.submit_button_text}<br>`;
            }
            if (text.bullet_points && Array.isArray(text.bullet_points)) {
                formatted += `<strong>Items:</strong><br>`;
                text.bullet_points.forEach(point => {
                    formatted += `• ${point}<br>`;
                });
            }
            
            // If we have formatted content, return it, otherwise fallback to JSON
            if (formatted) {
                return formatted.replace(/<br>$/, ''); // Remove trailing <br>
            } else {
                // Fallback: display as formatted JSON for any other object structure
                return `<pre style="font-size: 0.75em; white-space: pre-wrap;">${JSON.stringify(text, null, 2)}</pre>`;
            }
        }
        
        // Handle regular string text
        return text || 'No text provided';
    }

    previewHTML(encodedHtml) {
        const html = decodeURIComponent(encodedHtml);
        const newWindow = window.open('', '_blank');
        newWindow.document.write(html);
        newWindow.document.close();
    }

    copyToClipboard(encodedHtml) {
        const html = decodeURIComponent(encodedHtml);
        navigator.clipboard.writeText(html).then(() => {
            this.showMessage('✅ HTML copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = html;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showMessage('✅ HTML copied to clipboard!');
        });
    }

    displayCopyOptionsCompact(section_copy_data) {
        if (!section_copy_data) {
            return;
        }
        
        if (!section_copy_data.sections) {
            return;
        }

        const compactDiv = document.createElement('div');
        compactDiv.className = 'copy-options-compact';
        compactDiv.innerHTML = `
            <div class="compact-header">
                <h4><i class="fas fa-layer-group"></i> All Generated Copy Options</h4>
                <p>Review all copy variations with confidence scores and conversion insights</p>
            </div>
        `;

        const sectionsContainer = document.createElement('div');
        sectionsContainer.className = 'compact-sections-container';

        section_copy_data.sections.forEach((section, sectionIndex) => {
            if (section.copy_options && section.copy_options.length > 0) {
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'compact-section';
                
                let optionsHtml = '';
                section.copy_options.forEach((option, optionIndex) => {
                    const confidenceClass = option.confidence >= 90 ? 'high-confidence' : 
                                          option.confidence >= 80 ? 'medium-confidence' : 'low-confidence';
                    const rankBadge = optionIndex === 0 ? '<span class="rank-badge best">BEST</span>' :
                                     optionIndex === 1 ? '<span class="rank-badge good">GOOD</span>' :
                                     optionIndex === 2 ? '<span class="rank-badge ok">ALT</span>' :
                                     '<span class="rank-badge fallback">FALLBACK</span>';
                    
                    optionsHtml += `
                        <div class="compact-copy-option ${confidenceClass}">
                            <div class="compact-option-header">
                                ${rankBadge}
                                <span class="compact-confidence">${option.confidence}%</span>
                            </div>
                            <div class="compact-copy-text">${this.formatGeneratedText(option.generated_text)}</div>
                            <div class="compact-justification">
                                <i class="fas fa-lightbulb"></i>
                                ${option.justification}
                            </div>
                        </div>
                    `;
                });

                // Add section screenshot if available
                const sectionScreenshot = section.crop_image ? 
                    `<div class="compact-section-screenshot">
                        <img src="/uploads/${section.crop_image}" alt="${section.section_name} screenshot" 
                             onclick="copywritingAgent.enlargeImage('/uploads/${section.crop_image}', '${section.section_name}')"
                             title="Click to enlarge">
                    </div>` : '';

                sectionDiv.innerHTML = `
                    <div class="compact-section-header">
                        <h5>${section.section_name.replace('_', ' ').toUpperCase()}</h5>
                        <span class="section-purpose">${section.communicates}</span>
                    </div>
                    ${sectionScreenshot}
                    <div class="compact-options-grid">
                        ${optionsHtml}
                    </div>
                `;
                
                sectionsContainer.appendChild(sectionDiv);
            }
        });

        compactDiv.appendChild(sectionsContainer);
        
        // Always append the compact div, even if empty
        if (sectionsContainer.children.length === 0) {
            sectionsContainer.innerHTML = '<div style="padding: 1rem; text-align: center; color: #666;">No copy options found to display</div>';
        }
        
        this.resultsContent.appendChild(compactDiv);
    }

    setLoading(loading, message = 'Processing...', showProgress = false) {
        if (loading) {
            this.loadingState.style.display = 'block';
            document.getElementById('loadingTitle').textContent = message;
            this.generateBtn.disabled = true;
            this.generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            const progressSteps = document.getElementById('progressSteps');
            if (showProgress) {
                progressSteps.style.display = 'block';
                this.resetProgressSteps();
            } else {
                progressSteps.style.display = 'none';
            }
        } else {
            this.loadingState.style.display = 'none';
            document.getElementById('loadingTitle').textContent = 'Analyzing your design and generating copy...';
            document.getElementById('loadingDescription').textContent = 'Our AI is identifying sections and preparing copy generation';
            this.generateBtn.disabled = false;
            this.generateBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Design';
            document.getElementById('progressSteps').style.display = 'none';
        }
    }

    resetProgressSteps() {
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
            const status = step.querySelector('.step-status');
            status.classList.remove('active', 'completed');
            status.classList.add('pending');
        });
    }

    updateProgressStep(stepNumber, status = 'active', customMessage = null) {
        const step = document.querySelector(`[data-step="${stepNumber}"]`);
        const stepStatus = step.querySelector('.step-status');
        
        // Reset all steps to pending if starting over
        if (stepNumber === 1 && status === 'active') {
            this.resetProgressSteps();
        }
        
        // Update current step
        step.classList.remove('active', 'completed');
        stepStatus.classList.remove('active', 'completed', 'pending');
        
        if (status === 'active') {
            step.classList.add('active');
            stepStatus.classList.add('active');
        } else if (status === 'completed') {
            step.classList.add('completed');
            stepStatus.classList.add('completed');
        }

        // Update loading description
        const messages = {
            1: 'Using AI vision to identify page sections and their purposes...',
            2: 'Fetching brand data, voice guidelines, and context from Google Docs...',
            3: 'Analyzing sections and brand data to extract structured product information...',
            4: 'Using structured data and original screenshot to generate pixel-perfect HTML...',
            5: 'Processing results and preparing your complete landing page...'
        };

        if (customMessage) {
            document.getElementById('loadingDescription').textContent = customMessage;
        } else if (messages[stepNumber]) {
            document.getElementById('loadingDescription').textContent = messages[stepNumber];
        }
    }

    showResults() {
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
    }

    showError(message) {
        this.showSnackbar(message, 'error');
        // Also hide the old error display if it exists
        if (this.errorDisplay) {
            this.errorDisplay.style.display = 'none';
        }
    }

    hideError() {
        // Hide old error display if it exists
        if (this.errorDisplay) {
            this.errorDisplay.style.display = 'none';
        }
    }

    showAnalysisConfirmation(sections) {
        this.confirmationContent.innerHTML = '';
        
        // Group sections by component type for hierarchical display
        const componentGroups = this.groupSectionsByComponent(sections);
        
        // Add summary header
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'analysis-summary';
        summaryDiv.innerHTML = `
            <div class="summary-header">
                <p>Detected ${Object.keys(componentGroups).length} webpage component${Object.keys(componentGroups).length > 1 ? 's' : ''} with ${sections.length} text blocks • Review and confirm before generating copy</p>
            </div>
        `;
        this.confirmationContent.appendChild(summaryDiv);
        
        // Create grid container for components
        const componentsGrid = document.createElement('div');
        componentsGrid.className = 'components-grid';
        
        // Display each component with its text blocks
        Object.entries(componentGroups).forEach(([componentKey, componentData]) => {
            const componentDiv = document.createElement('div');
            componentDiv.className = 'component-analysis';
            
            // Component header
            const componentHeader = document.createElement('div');
            componentHeader.className = 'component-header';
            componentHeader.innerHTML = `
                <div class="component-info">
                    <div class="component-name">${componentData.name}</div>
                    <div class="component-type">${componentData.type}</div>
                    </div>
                <div class="component-stats">${componentData.sections.length} text blocks</div>
            `;
            componentDiv.appendChild(componentHeader);
            
            // Text blocks within this component
            const blocksContainer = document.createElement('div');
            blocksContainer.className = 'text-blocks-container';
            
            componentData.sections.forEach((section, blockIndex) => {
                const globalIndex = sections.findIndex(s => s.id === section.id);
                const blockDiv = this.createTextBlockElement(section, blockIndex, globalIndex);
                blocksContainer.appendChild(blockDiv);
            });
            
            componentDiv.appendChild(blocksContainer);
            componentsGrid.appendChild(componentDiv);
        });

        // Append the grid to confirmation content
        this.confirmationContent.appendChild(componentsGrid);

        // Add additional context section
        const contextDiv = document.createElement('div');
        contextDiv.className = 'context-section';
        contextDiv.innerHTML = `
            <div class="context-header">
                <h4><i class="fas fa-comment-alt"></i> Additional Context</h4>
            </div>
            <div class="context-content">
                <textarea id="confirmationContext" placeholder="Add any additional context about these sections or the overall page..." rows="3">${this.additionalContext.value}</textarea>
                <p class="context-hint">💡 This context will be used when generating copy for all sections</p>
            </div>
        `;
        this.confirmationContent.appendChild(contextDiv);
        
        this.confirmationSection.style.display = 'block';
        this.confirmationSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideConfirmation() {
        this.confirmationSection.style.display = 'none';
    }

    enableEditing() {
        const sections = this.confirmationContent.querySelectorAll('.section-analysis');
        
        sections.forEach(sectionDiv => {
            const purposeValue = sectionDiv.querySelector('.purpose-value');
            const structureValue = sectionDiv.querySelector('.structure-value');
            const currentTextValue = sectionDiv.querySelector('.current-text-value');
            
            // Convert to editable textareas
            purposeValue.innerHTML = `<textarea class="editable-analysis" data-field="purpose">${purposeValue.textContent}</textarea>`;
            structureValue.innerHTML = `<textarea class="editable-analysis" data-field="text_structure">${structureValue.textContent}</textarea>`;
            currentTextValue.innerHTML = `<textarea class="editable-analysis" data-field="current_text">${currentTextValue.textContent}</textarea>`;
        });

        // Update button text
        this.editAnalysisBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        this.editAnalysisBtn.onclick = () => this.saveEdits();
    }

    saveEdits() {
        const sections = this.confirmationContent.querySelectorAll('.section-analysis');
        
        sections.forEach((sectionDiv, index) => {
            const textareas = sectionDiv.querySelectorAll('.editable-analysis');
            
            textareas.forEach(textarea => {
                const field = textarea.dataset.field;
                const value = textarea.value.trim();
                
                // Update the stored sections data
                this.analyzedSections[index][field] = value;
                
                // Convert back to display format
                const parent = textarea.parentElement;
                parent.innerHTML = value || (field === 'current_text' ? 'No text detected' : value);
                parent.className = 'analysis-value ' + field.replace('_', '-') + '-value';
            });
        });

        // Reset button
        this.editAnalysisBtn.innerHTML = '<i class="fas fa-edit"></i> Edit Analysis';
        this.editAnalysisBtn.onclick = () => this.enableEditing();
        
        this.showMessage('✅ Analysis updated successfully!');
    }

    async proceedWithCopyGeneration() {
        this.setLoading(true, 'Generating brand-perfect copy...', true);
        this.hideConfirmation();
        this.hideError();

        try {
            // Generate copy with confirmed/edited sections with progress updates
            await this.generateCopyWithProgress(this.analyzedSections);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = error.message || 'An error occurred while generating copy. Please try again.';
            console.log('Showing error message:', errorMessage);
            this.showError(errorMessage);
            this.showAnalysisConfirmation(this.analyzedSections); // Show confirmation again on error
        } finally {
            this.setLoading(false);
        }
    }

    async processDocument() {
        try {
            console.log('🔄 Starting document processing...');
            this.updateProgressStep(1, 'active');
            
            const formData = new FormData();
            const brandName = this.getBrandName();
            
            console.log('📄 Document upload details:', {
                hasDocsFile: !!this.uploadedDocs,
                hasDocsUrl: !!this.uploadedDocsUrl,
                brandName: brandName
            });
            
            if (this.uploadedDocs) {
                console.log('📎 Processing uploaded file:', this.uploadedDocs.name);
                formData.append('document', this.uploadedDocs);
                formData.append('type', 'file');
            } else if (this.uploadedDocsUrl) {
                console.log('🔗 Processing URL:', this.uploadedDocsUrl);
                formData.append('url', this.uploadedDocsUrl);
                formData.append('type', 'url');
            } else {
                throw new Error('No document file or URL provided');
            }
            
            formData.append('brand_name', brandName);
            formData.append('additional_context', this.additionalContext.value);
            
            console.log('🚀 Sending request to /api/process-document...');
            
            const response = await fetch('/api/process-document', {
                method: 'POST',
                body: formData
            });

            console.log('📡 Response received:', response.status, response.statusText);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Server error:', errorText);
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('✅ Document processing response:', data);
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to process document');
            }

            this.updateProgressStep(1, 'completed');
            
            // Go directly to copy generation for documents (no section confirmation needed)
            console.log('📝 Going directly to copy generation from document content...');
            this.updateProgressStep(2, 'active');
            await this.generateCopyFromDocument(data);
            
        } catch (error) {
            console.error('❌ Error processing document:', error);
            throw error;
        }
    }

    async generateCopyFromDocument(documentData) {
        try {
            this.updateProgressStep(2, 'completed');
            this.updateProgressStep(3, 'active');
            
            const payload = {
                document_content: documentData.content,
                brand_name: this.getBrandName(),
                additional_context: this.additionalContext.value,
                document_type: 'processed'
            };

            const response = await fetch('/api/generate-copy-from-document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Failed to generate copy from document');
            }

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Failed to generate copy from document');
            }

            this.updateProgressStep(3, 'completed');
            this.updateProgressStep(4, 'active');
            await this.delay(300);
            this.updateProgressStep(4, 'completed');
            this.updateProgressStep(5, 'active');
            
            this.displayResults(data);
            
            await this.delay(200);
            this.updateProgressStep(5, 'completed');
            
        } catch (error) {
            console.error('Error generating copy from document:', error);
            throw error;
        }
    }

    showSnackbar(message, type = 'success', duration = 3000) {
        console.log('showSnackbar called:', message, type);
        
        // Remove any existing snackbar
        const existingSnackbar = document.querySelector('.snackbar');
        if (existingSnackbar) {
            existingSnackbar.remove();
        }

        // Create new snackbar
        const snackbar = document.createElement('div');
        snackbar.className = `snackbar ${type}`;
        snackbar.textContent = message;
        
        document.body.appendChild(snackbar);
        console.log('Snackbar added to DOM:', snackbar);

        // Trigger animation
        setTimeout(() => {
            snackbar.classList.add('show');
            console.log('Snackbar show class added');
        }, 10);

        // Auto-hide after duration
        setTimeout(() => {
            snackbar.classList.remove('show');
            setTimeout(() => {
                if (snackbar.parentNode) {
                    snackbar.remove();
                }
            }, 400);
        }, duration);
    }

    showMessage(message) {
        this.showSnackbar(message, 'success');
    }

    showInfo(message) {
        this.showSnackbar(message, 'info');
    }

    showAddSectionModal() {
        this.addSectionModal.classList.add('show');
        // Reset form
        document.getElementById('addSectionForm').reset();
        // Auto-generate next section ID
        const existingIds = this.analyzedSections.map(s => s.id);
        let nextId = `section_${this.analyzedSections.length + 1}`;
        let counter = this.analyzedSections.length + 1;
        
        // Ensure unique ID
        while (existingIds.includes(nextId)) {
            counter++;
            nextId = `section_${counter}`;
        }
        
        document.getElementById('sectionId').value = nextId;
        
        // Add escape key listener
        document.addEventListener('keydown', this.handleModalEscape.bind(this));
        
        // Add click outside to close
        this.addSectionModal.addEventListener('click', this.handleModalOutsideClick.bind(this));
    }

    handleModalEscape(e) {
        if (e.key === 'Escape' && this.addSectionModal.classList.contains('show')) {
            closeAddSectionModal();
        }
    }

    handleModalOutsideClick(e) {
        if (e.target === this.addSectionModal) {
            closeAddSectionModal();
        }
    }

    removeSection(index) {
        if (this.analyzedSections.length <= 1) {
            alert('Cannot remove the last section. At least one section is required.');
            return;
        }
        
        if (confirm(`Are you sure you want to remove ${this.analyzedSections[index].id}?`)) {
            this.analyzedSections.splice(index, 1);
            this.showAnalysisConfirmation(this.analyzedSections);
            this.showMessage('Section removed successfully!');
        }
    }

    enlargeImage(imageSrc, sectionId) {
        // Create modal for enlarged image
        const modal = document.createElement('div');
        modal.className = 'modal-overlay show';
        modal.style.zIndex = '1001';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 80%; max-height: 80%;">
                <div class="modal-header">
                    <h3><i class="fas fa-expand"></i> ${sectionId.replace('_', ' ').toUpperCase()} Screenshot</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div style="padding: 1rem; text-align: center; background: var(--bg-secondary);">
                    <img src="${imageSrc}" style="max-width: 100%; height: auto; border-radius: var(--radius-md); box-shadow: var(--shadow-lg);">
                </div>
            </div>
        `;
        
        // Add click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Add escape key to close
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        document.body.appendChild(modal);
    }

    toggleDebug(sectionId) {
        const debugElement = document.getElementById(`debug-${sectionId}`);
        if (debugElement) {
            if (debugElement.classList.contains('hide')) {
                debugElement.classList.remove('hide');
                debugElement.classList.add('show');
            } else {
                debugElement.classList.remove('show');
                debugElement.classList.add('hide');
            }
        }
    }

    adjustCoordinates(sectionId, sectionIndex) {
        const section = this.analyzedSections[sectionIndex];
        if (!section || !section.bounding_box) return;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay show';
        modal.style.zIndex = '1001';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3><i class="fas fa-crosshairs"></i> Adjust Coordinates - ${sectionId.replace('_', ' ').toUpperCase()}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <p style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.9rem;">
                        Adjust the bounding box coordinates as percentages (0-100) of the total image dimensions.
                    </p>
                    <div class="modal-form-group">
                        <label>X Position (left edge %)</label>
                        <input type="number" id="coord-x" min="0" max="100" step="0.1" value="${section.bounding_box.x}">
                    </div>
                    <div class="modal-form-group">
                        <label>Y Position (top edge %)</label>
                        <input type="number" id="coord-y" min="0" max="100" step="0.1" value="${section.bounding_box.y}">
                    </div>
                    <div class="modal-form-group">
                        <label>Width (%)</label>
                        <input type="number" id="coord-width" min="1" max="100" step="0.1" value="${section.bounding_box.width}">
                    </div>
                    <div class="modal-form-group">
                        <label>Height (%)</label>
                        <input type="number" id="coord-height" min="1" max="100" step="0.1" value="${section.bounding_box.height}">
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="modal-btn cancel" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button type="button" class="modal-btn primary" onclick="copywritingAgent.saveCoordinates('${sectionId}', ${sectionIndex}, this.closest('.modal-overlay'))">
                        Update & Re-crop
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async saveCoordinates(sectionId, sectionIndex, modal) {
        const x = parseFloat(document.getElementById('coord-x').value);
        const y = parseFloat(document.getElementById('coord-y').value);
        const width = parseFloat(document.getElementById('coord-width').value);
        const height = parseFloat(document.getElementById('coord-height').value);
        
        // Validate coordinates
        if (x < 0 || x >= 100 || y < 0 || y >= 100 || width <= 0 || height <= 0) {
            alert('Please enter valid coordinates (0-100 for position, >0 for dimensions)');
            return;
        }
        
        if (x + width > 100 || y + height > 100) {
            alert('Section extends beyond image boundaries. Please adjust coordinates.');
            return;
        }
        
        // Update the section's bounding box
        this.analyzedSections[sectionIndex].bounding_box = { x, y, width, height };
        
        // Close modal
        modal.remove();
        
        // Show loading state
        this.showMessage('Re-cropping section with new coordinates...', 'info');
        
        try {
            // Re-crop the section with new coordinates
            const response = await fetch('/api/recrop-section', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_path: this.uploadedImageName,
                    section_id: sectionId,
                    bounding_box: { x, y, width, height }
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                // Update the section with the new crop image
                this.analyzedSections[sectionIndex].crop_image = result.crop_image;
                this.showAnalysisConfirmation(this.analyzedSections);
                this.showMessage('✅ Section re-cropped with new coordinates!');
            } else {
                const error = await response.json();
                this.showAnalysisConfirmation(this.analyzedSections);
                this.showMessage(`❌ ${error.error || 'Failed to re-crop section'}`, 'error');
            }
        } catch (error) {
            this.showAnalysisConfirmation(this.analyzedSections);
            this.showMessage('❌ Error updating coordinates: ' + error.message, 'error');
        }
    }

    groupSectionsByComponent(sections) {
        const groups = {};
        
        sections.forEach(section => {
            const componentType = section.component_type || 'content';
            const componentName = section.component_name || 'Content Section';
            const componentKey = `${componentType}_${componentName.replace(/\s+/g, '_')}`;
            
            if (!groups[componentKey]) {
                groups[componentKey] = {
                    type: componentType,
                    name: componentName,
                    sections: []
                };
            }
            
            groups[componentKey].sections.push(section);
        });
        
        return groups;
    }

    createTextBlockElement(section, blockIndex, globalIndex) {
        const blockDiv = document.createElement('div');
        blockDiv.className = 'text-block-analysis';
        blockDiv.dataset.index = globalIndex;
        
        // Create screenshot section
        const coordinateDebug = section.bounding_box ? 
            `<div class="coordinate-debug hide" id="debug-${section.id}">
                📍 Coordinates: x=${section.bounding_box.x}%, y=${section.bounding_box.y}%, w=${section.bounding_box.width}%, h=${section.bounding_box.height}%
            </div>` : '';

        const coordinateTools = `
            <div class="coordinate-tools">
                <button class="debug-toggle" onclick="copywritingAgent.toggleDebug('${section.id}')">
                    <i class="fas fa-crosshairs"></i> Coords
                </button>
                ${section.bounding_box ? `<button class="adjust-coords-btn" onclick="copywritingAgent.adjustCoordinates('${section.id}', ${globalIndex})">
                    <i class="fas fa-edit"></i> Adjust
                </button>` : ''}
            </div>`;

        const screenshotHtml = section.crop_image ? 
            `<div class="section-screenshot" onclick="copywritingAgent.enlargeImage('/uploads/${section.crop_image}', '${section.id}')">
                <img src="/uploads/${section.crop_image}" alt="Block ${section.block_id} screenshot" title="Click to enlarge">
                ${coordinateDebug}
                ${coordinateTools}
            </div>` :
            `<div class="no-screenshot">
                <i class="fas fa-image"></i>&nbsp; No screenshot available
                ${coordinateDebug}
                ${coordinateTools}
            </div>`;
        
        blockDiv.innerHTML = `
            <div class="block-content">
                <div class="block-header">
                    <div class="block-info">
                        <div class="block-id">Block ${blockIndex + 1}</div>
                        <div class="block-stats">${section.word_count || 'N/A'} words</div>
                    </div>
                    <button class="block-manage-btn" onclick="copywritingAgent.removeSection(${globalIndex})" title="Remove this text block">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                ${screenshotHtml}
                <div class="block-details">
                    <div class="block-row">
                        <div class="block-label">Text content:</div>
                        <div class="block-value current-text-value">${section.current_text || section.text || 'No text detected'}</div>
                    </div>
                    <div class="block-row">
                        <div class="block-label">🎯 Purpose:</div>
                        <div class="block-value purpose-value">${section.purpose || 'General content'}</div>
                    </div>
                    <div class="block-row">
                        <div class="block-label">Structure needed:</div>
                        <div class="block-value structure-value">${typeof section.text_structure === 'object' ? JSON.stringify(section.text_structure) : (section.text_structure || 'Standard text')}</div>
                    </div>
                </div>
            </div>
        `;
        
        return blockDiv;
    }
}

// Global functions for modal (accessible from HTML onclick handlers)
function closeAddSectionModal() {
    const modal = document.getElementById('addSectionModal');
    modal.classList.remove('show');
    
    // Remove event listeners to prevent memory leaks
    document.removeEventListener('keydown', copywritingAgent.handleModalEscape);
    modal.removeEventListener('click', copywritingAgent.handleModalOutsideClick);
}

function addNewSection() {
    const form = document.getElementById('addSectionForm');
    
    // Validate form
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get form values
    const newSection = {
        id: document.getElementById('sectionId').value.trim(),
        type: document.getElementById('sectionType').value,
        purpose: document.getElementById('sectionPurpose').value.trim(),
        text_structure: document.getElementById('sectionStructure').value.trim(),
        location: document.getElementById('sectionLocation').value.trim(),
        current_text: document.getElementById('sectionCurrentText').value.trim() || ''
    };
    
    // Validate ID uniqueness
    if (copywritingAgent.analyzedSections.some(section => section.id === newSection.id)) {
        alert('Section ID already exists. Please choose a different ID.');
        return;
    }
    
    // Validate ID format
    if (!/^[a-z_]+$/.test(newSection.id)) {
        alert('Section ID must contain only lowercase letters and underscores.');
        return;
    }
    
    // Add default bounding box and no crop image for manually added sections
    newSection.bounding_box = {"x": 0, "y": 0, "width": 100, "height": 100};
    newSection.crop_image = null;
    
    // Add section
    copywritingAgent.analyzedSections.push(newSection);
    
    // Refresh display
    copywritingAgent.showAnalysisConfirmation(copywritingAgent.analyzedSections);
    
    // Close modal
    closeAddSectionModal();
    
    // Show success message
    copywritingAgent.showMessage(`Section "${newSection.id}" added successfully!`);
}

// Make copywritingAgent globally accessible
let copywritingAgent;

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    copywritingAgent = new CopywritingAgent();
}); 