'use client'

import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import Image from 'next/image'
import Snackbar from '../components/Snackbar'
import Lightbox from '../components/Lightbox'
import SectionEditor from '../components/SectionEditor'
import { useSnackbar } from '../hooks/useSnackbar'

interface Brand {
  name: string
}

interface Section {
  id: string
  type: string
  purpose: string
  text_structure: string
  location: string
  current_text: string
  crop_image?: string
  bounding_box?: {
    x: number
    y: number
    width: number
    height: number
  }
}

interface CopyOption {
  generated_text: string
  confidence: number
  justification: string
}

interface SectionCopyData {
  sections?: Array<{
    section_name: string
    communicates: string
    text_structure: string
    copy_options: CopyOption[]
    crop_image?: string
  }>
  ideas?: string
  detailed_copy?: string
  product_data?: any
  multiple_products?: boolean
  product_count?: number
  products?: any[]
  summary?: string
  structured_data?: {
    products: Array<{
      product_id: string
      product_name: {
        original: string
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      taglines: {
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      headlines: {
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      claims: {
        original: string[]
        variations: Array<{
          claims: string[]
          angle: string
          confidence: number
          justification: string
        }>
      }
      description: {
        original: string
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      key_benefits: Array<{
        title: string
        description: string
        supporting_ingredients: string[]
      }>
      instructions: {
        original: string
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      call_to_action: {
        options: Array<{
          text: string
          angle: string
          confidence: number
          justification: string
        }>
      }
      volume: string
      why_it_works: string
      copy_variations: Array<{
        angle: string
        headline: string
        description: string
      }>
      competitive_advantages: string[]
      target_audience_insights: string
      emotional_triggers: string[]
      brand_context: {
        brand_name: string
        brand_voice: string
        target_audience: string
      }
      generated_at: string
    }>
  }
}

export default function Home() {
  // Snackbar hook
  const { snackbar, showSuccess, showError, showWarning, showInfo, hideSnackbar } = useSnackbar()

  // State management
  const [brands, setBrands] = useState<string[]>([])
  const [selectedBrand, setSelectedBrand] = useState('')
  const [customBrand, setCustomBrand] = useState('')
  const [brandType, setBrandType] = useState<'existing' | 'custom'>('existing')
  const [uploadType, setUploadType] = useState<'image' | 'docs'>('image')
  const [additionalContext, setAdditionalContext] = useState('')
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [uploadedDocs, setUploadedDocs] = useState<File | null>(null)
  
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [sections, setSections] = useState<Section[]>([])
  const [imagePath, setImagePath] = useState<string>('')
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [showResults, setShowResults] = useState(false)
  const [lightboxImage, setLightboxImage] = useState<{ src: string; alt: string } | null>(null)
  const [sectionEditor, setSectionEditor] = useState<{ isOpen: boolean; section?: Section; isNew: boolean }>({
    isOpen: false,
    section: undefined,
    isNew: false
  })

  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set())

  // Refs
  const imageInputRef = useRef<HTMLInputElement>(null)
  const docsInputRef = useRef<HTMLInputElement>(null)
  const loadingRef = useRef<HTMLDivElement>(null)
  const confirmationRef = useRef<HTMLDivElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // API URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

  // Load brands on component mount
  useEffect(() => {
    loadBrands()
  }, [])

  useEffect(() => {
    if (loading) {
      loadingRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [loading])

  useEffect(() => {
    if (showConfirmation) {
      confirmationRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [showConfirmation])

  useEffect(() => {
    if (showResults) {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [showResults])

  const loadBrands = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/brands`)
      setBrands(response.data.brands || [])
    } catch (error) {
      console.error('Error loading brands:', error)
      showError('Failed to load brands. Please refresh the page.')
    }
  }

  const handleImageClick = (src: string, alt: string) => {
    setLightboxImage({ src, alt })
  }

  const closeLightbox = () => {
    setLightboxImage(null)
  }

  const getConfidenceClass = (confidence: number) => {
    if (confidence >= 90) return 'high-confidence'
    if (confidence >= 80) return 'medium-confidence'
    return 'low-confidence'
  }

  const toggleSection = (sectionId: string) => {
    const newCollapsed = new Set(collapsedSections)
    if (newCollapsed.has(sectionId)) {
      newCollapsed.delete(sectionId)
    } else {
      newCollapsed.add(sectionId)
    }
    setCollapsedSections(newCollapsed)
  }

  const openSectionEditor = (section?: Section, isNew: boolean = false) => {
    setSectionEditor({
      isOpen: true,
      section: section,
      isNew: isNew
    })
  }

  const closeSectionEditor = () => {
    setSectionEditor({
      isOpen: false,
      section: undefined,
      isNew: false
    })
  }

  const handleSectionSave = (updatedSection: Section) => {
    if (sectionEditor.isNew) {
      // Add new section
      setSections(prev => [...prev, updatedSection])
      showSuccess(`New section "${updatedSection.id}" added successfully!`)
    } else {
      // Update existing section
      setSections(prev => 
        prev.map(section => 
          section.id === updatedSection.id ? updatedSection : section
        )
      )
      showSuccess(`Section "${updatedSection.id}" updated successfully!`)
    }
  }

  const handleSectionDelete = (sectionId: string) => {
    if (confirm(`Are you sure you want to delete section "${sectionId}"?`)) {
      setSections(prev => prev.filter(section => section.id !== sectionId))
      showSuccess(`Section "${sectionId}" deleted successfully!`)
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      handleFile(files[0], 'image')
    }
  }

  const handleDocsUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      handleFile(files[0], 'docs')
    }
  }

  const handleFile = (file: File, type: 'image' | 'docs') => {
    if (type === 'image') {
      if (!file.type.startsWith('image/')) {
        showWarning('Please select an image file (PNG, JPG, WEBP)')
        return
      }
      if (file.size > 16 * 1024 * 1024) {
        showWarning('File size must be less than 16MB')
        return
      }
      setUploadedImage(file)
      setUploadedDocs(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      
      showSuccess(`Image "${file.name}" uploaded successfully!`)
    } else {
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/pdf',
        'text/plain'
      ]
      
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(docx|doc|pdf|txt)$/i)) {
        showWarning('Please select a document file (DOCX, DOC, PDF, TXT)')
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        showWarning('Document size must be less than 10MB')
        return
      }
      setUploadedDocs(file)
      setUploadedImage(null)
      setPreviewImage(null)
      
      showSuccess(`Document "${file.name}" uploaded successfully!`)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.add('dragover')
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.remove('dragover')
  }

  const handleDrop = (e: React.DragEvent, type: 'image' | 'docs') => {
    e.preventDefault()
    e.currentTarget.classList.remove('dragover')
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0], type)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (uploadType === 'image' && !uploadedImage) {
      showWarning('Please upload an image first.')
      return
    }
    
    if (uploadType === 'docs' && !uploadedDocs) {
      showWarning('Please upload a document')
      return
    }
    
    const brandName = brandType === 'existing' ? selectedBrand : customBrand
    if (!brandName) {
      showWarning(brandType === 'existing' ? 'Please select a brand.' : 'Please enter a custom client name.')
      return
    }

    setLoading(true)
    setShowConfirmation(false)
    setShowResults(false)

    try {
      if (uploadType === 'image') {
        await analyzeImage()
      } else {
        await processDocument()
      }
    } catch (error: any) {
      console.error('Error:', error)
      showError(error.message || 'An error occurred while processing. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const analyzeImage = async () => {
    if (!uploadedImage) return

    const formData = new FormData()
    formData.append('image', uploadedImage)

    const response = await axios.post(`${API_URL}/api/analyze-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    if (response.data.success) {
      setSections(response.data.sections)
      setImagePath(response.data.image_path)
      setShowConfirmation(true)
      showInfo(`Found ${response.data.sections.length} sections in your image`)
    } else {
      throw new Error(response.data.error || 'Failed to analyze image')
    }
  }

  const processDocument = async () => {
    const formData = new FormData()
    const brandName = brandType === 'existing' ? selectedBrand : customBrand
    
    if (uploadedDocs) {
      formData.append('document', uploadedDocs)
      formData.append('type', 'file')
    }
    
    formData.append('brand_name', brandName)
    formData.append('additional_context', additionalContext)

    const response = await axios.post(`${API_URL}/api/process-document`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    if (response.data.success) {
      await generateCopyFromDocument(response.data)
    } else {
      throw new Error(response.data.error || 'Failed to process document')
    }
  }

  const generateCopyFromDocument = async (documentData: any) => {
    const brandName = brandType === 'existing' ? selectedBrand : customBrand
    
    const payload = {
      document_content: documentData.content,
      brand_name: brandName,
      additional_context: additionalContext,
      document_type: 'processed'
    }

    const response = await axios.post(`${API_URL}/api/generate-copy-from-document`, payload, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    console.log('📡 Response received:', response);

    if (response.data.success) {
      setResults(response.data)
      setShowResults(true)
      showSuccess('Copy generated successfully from your document!')
    } else {
      throw new Error(response.data.error || 'Failed to generate copy from document')
    }
  }

  const confirmAnalysis = async () => {
    const brandName = brandType === 'existing' ? selectedBrand : customBrand
    
    const payload = {
      sections: sections,
      brand_name: brandName,
      additional_context: additionalContext,
      image_path: imagePath
    }

    setLoading(true)
    setShowConfirmation(false)

    try {
      const response = await axios.post(`${API_URL}/api/generate-copy`, payload, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.data.success) {
        setResults(response.data)
        setShowResults(true)
        showSuccess('Brand-perfect copy generated successfully!')
      } else {
        throw new Error(response.data.error || 'Failed to generate copy')
      }
    } catch (error: any) {
      console.error('Error:', error)
      showError(error.message || 'An error occurred while generating copy. Please try again.')
      setShowConfirmation(true) // Show confirmation again on error
    } finally {
      setLoading(false)
    }
  }

  const renderResults = () => {
    if (!results) return null

    const sectionCopyData: SectionCopyData = results.section_copy_data || {}

    return (
      <div ref={resultsRef} className="results" style={{ display: showResults ? 'block' : 'none' }}>
        <div className="results-header">
          <h2><i className="fas fa-check-circle"></i> Your Brand-Perfect Copy is Ready!</h2>
        </div>
        <div className="results-content">
                    {/* Document pipeline results */}
          {results.pipeline_version === 'document' && (
            <div className="detailed-copy-content">
              <div className="copy-section">
                <div className="products-grid">
                  {/* Use structured data if available, otherwise fallback to parsing markdown */}
                  {sectionCopyData.structured_data?.products ? 
                    sectionCopyData.structured_data.products.map((product: any, index: number) => (
                      <div key={index} className="product-card">
                        <div className="product-header">
                          <h2 className="product-title">{product.product_name.original}</h2>
                          <div className="product-controls">
                            <button 
                              className="collapse-toggle-btn"
                              onClick={() => {
                                const allSections = ['product-name', 'taglines', 'headlines', 'claims', 'description', 'benefits', 'instructions', 'cta', 'volume', 'why-it-works', 'copy-variations', 'marketing-intelligence']
                                const allCollapsed = allSections.every(section => collapsedSections.has(section))
                                if (allCollapsed) {
                                  setCollapsedSections(new Set())
                                } else {
                                  setCollapsedSections(new Set(allSections))
                                }
                              }}
                            >
                              {['product-name', 'taglines', 'headlines', 'claims', 'description', 'benefits', 'instructions', 'cta', 'volume', 'why-it-works', 'copy-variations', 'marketing-intelligence'].every(section => collapsedSections.has(section)) ? 'Expand All' : 'Collapse All'}
                            </button>
                          </div>
                        </div>
                        <div className="product-content">
                          <div className="structured-product-content">
                            
                            {/* Product Name Options */}
                            <div className={`product-section ${collapsedSections.has('product-name') ? 'collapsed' : ''}`}>
                              <h4 onClick={() => toggleSection('product-name')}>Product Name Options</h4>
                              <div className="copy-options">
                                {product.product_name.options.map((option: any, i: number) => (
                                  <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                    <div className="option-header">
                                      <span className="option-label">{option.angle}</span>
                                      <span className="confidence-score">{option.confidence}%</span>
                                    </div>
                                    <div className="option-text product-name-option">{option.text}</div>
                                    <div className="option-justification">{option.justification}</div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Taglines */}
                            {product.taglines?.options && product.taglines.options.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('taglines') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('taglines')}>Tagline Options</h4>
                                <div className="copy-options">
                                  {product.taglines.options.map((option: any, i: number) => (
                                    <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                      <div className="option-header">
                                        <span className="option-label">{option.angle}</span>
                                        <span className="confidence-score">{option.confidence}%</span>
                                      </div>
                                      <div className="option-text tagline-option">{option.text}</div>
                                      <div className="option-justification">{option.justification}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Headlines */}
                            {product.headlines?.options && product.headlines.options.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('headlines') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('headlines')}>Headline Options</h4>
                                <div className="copy-options">
                                  {product.headlines.options.map((option: any, i: number) => (
                                    <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                      <div className="option-header">
                                        <span className="option-label">{option.angle}</span>
                                        <span className="confidence-score">{option.confidence}%</span>
                                      </div>
                                      <div className="option-text headline-option">{option.text}</div>
                                      <div className="option-justification">{option.justification}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Claims Variations */}
                            {product.claims?.variations && product.claims.variations.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('claims') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('claims')}>Claims Variations</h4>
                                <div className="copy-options">
                                  {product.claims.variations.map((variation: any, i: number) => (
                                    <div key={i} className={`copy-option ${getConfidenceClass(variation.confidence)}`}>
                                      <div className="option-header">
                                        <span className="option-label">{variation.angle}</span>
                                        <span className="confidence-score">{variation.confidence}%</span>
                                      </div>
                                      <div className="claims-list">
                                        {variation.claims.map((claim: string, j: number) => (
                                          <span key={j} className="claim-tag">{claim}</span>
                                        ))}
                                      </div>
                                      <div className="option-justification">{variation.justification}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Description with options */}
                            <div className={`product-section ${collapsedSections.has('description') ? 'collapsed' : ''}`}>
                              <h4 onClick={() => toggleSection('description')}>Product Description Options</h4>
                              <div className="copy-options">
                                {product.description.options.map((option: any, i: number) => (
                                  <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                    <div className="option-header">
                                      <span className="option-label">{option.angle}</span>
                                      <span className="confidence-score">{option.confidence}%</span>
                                    </div>
                                    <div className="option-text">{option.text}</div>
                                    <div className="option-justification">{option.justification}</div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Key Benefits */}
                            {product.key_benefits && product.key_benefits.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('benefits') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('benefits')}>Key Benefits</h4>
                                {product.key_benefits.map((benefit: any, i: number) => (
                                  <div key={i} className="benefit-item">
                                    <h5>{benefit.title}</h5>
                                    <p>{benefit.description}</p>
                                    {benefit.supporting_ingredients && benefit.supporting_ingredients.length > 0 && (
                                      <div className="ingredients-list">
                                        <strong>Key Ingredients:</strong> {benefit.supporting_ingredients.join(', ')}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Instructions with options */}
                            {product.instructions.options && product.instructions.options.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('instructions') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('instructions')}>Usage Instructions Options</h4>
                                <div className="copy-options">
                                  {product.instructions.options.map((option: any, i: number) => (
                                    <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                      <div className="option-header">
                                        <span className="option-label">{option.angle}</span>
                                        <span className="confidence-score">{option.confidence}%</span>
                                      </div>
                                      <div className="option-text">{option.text}</div>
                                      <div className="option-justification">{option.justification}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Call to Action Options */}
                            {product.call_to_action?.options && product.call_to_action.options.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('cta') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('cta')}>Call to Action Options</h4>
                                <div className="copy-options">
                                  {product.call_to_action.options.map((option: any, i: number) => (
                                    <div key={i} className={`copy-option ${getConfidenceClass(option.confidence)}`}>
                                      <div className="option-header">
                                        <span className="option-label">{option.angle}</span>
                                        <span className="confidence-score">{option.confidence}%</span>
                                      </div>
                                      <div className="option-text cta-option">{option.text}</div>
                                      <div className="option-justification">{option.justification}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Volume */}
                            {product.volume && (
                              <div className={`product-section ${collapsedSections.has('volume') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('volume')}>Volume</h4>
                                <div className="volume-info">{product.volume}</div>
                              </div>
                            )}

                            {/* Why It Works */}
                            {product.why_it_works && (
                              <div className={`product-section ${collapsedSections.has('why-it-works') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('why-it-works')}>Why It Works</h4>
                                <p>{product.why_it_works}</p>
                              </div>
                            )}

                            {/* Copy Variations */}
                            {product.copy_variations && product.copy_variations.length > 0 && (
                              <div className={`product-section ${collapsedSections.has('copy-variations') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('copy-variations')}>Alternative Copy Angles</h4>
                                {product.copy_variations.map((variation: any, i: number) => (
                                  <div key={i} className="variation-item">
                                    <h5>{variation.angle}</h5>
                                    <div className="variation-headline">"{variation.headline}"</div>
                                    <p>{variation.description}</p>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Additional Product Info */}
                            {(product.competitive_advantages?.length > 0 || product.target_audience_insights || product.emotional_triggers?.length > 0) && (
                              <div className={`product-section ${collapsedSections.has('marketing-intelligence') ? 'collapsed' : ''}`}>
                                <h4 onClick={() => toggleSection('marketing-intelligence')}>Marketing Intelligence</h4>
                                
                                {product.competitive_advantages && product.competitive_advantages.length > 0 && (
                                  <div className="marketing-subsection">
                                    <h5>Competitive Advantages</h5>
                                    <ul className="advantages-list">
                                      {product.competitive_advantages.map((advantage: string, i: number) => (
                                        <li key={i}>{advantage}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {product.target_audience_insights && (
                                  <div className="marketing-subsection">
                                    <h5>Target Audience Insights</h5>
                                    <p>{product.target_audience_insights}</p>
                                  </div>
                                )}

                                {product.emotional_triggers && product.emotional_triggers.length > 0 && (
                                  <div className="marketing-subsection">
                                    <h5>Emotional Triggers</h5>
                                    <div className="triggers-list">
                                      {product.emotional_triggers.map((trigger: string, i: number) => (
                                        <span key={i} className="trigger-tag">{trigger}</span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )) :
                    /* Fallback - show message if no structured data */
                    <div className="product-card">
                      <div className="product-header">
                        <h2 className="product-title">Processing Complete</h2>
                      </div>
                      <div className="product-content">
                        <p>✅ {sectionCopyData.summary || 'Copy generation completed successfully'}</p>
                        <p>📊 Generated structured copy data with multiple options for each product element.</p>
                        {sectionCopyData.product_count && (
                          <p>🛍️ Products processed: {sectionCopyData.product_count}</p>
                        )}
                      </div>
                    </div>
                  }
                </div>
              </div>
            </div>
          )}

          {/* Improvement ideas */}
          {sectionCopyData.ideas && (
            <div className="improvement-ideas">
              <div className="ideas-section">
                <h4><i className="fas fa-lightbulb"></i> Strategic Improvement Insights</h4>
                <div className="ideas-content">
                  <p>{sectionCopyData.ideas}</p>
                </div>
              </div>
            </div>
          )}

          {/* Image pipeline results */}
          {sectionCopyData.sections && (
            <div className="section-copy-display">
              <div className="data-section">
                <h4><i className="fas fa-edit"></i> Generated Section Copy</h4>
                <div className="data-content">
                  {sectionCopyData.sections.map((section, index) => (
                    <div key={index} className="section-copy-item">
                      <div className="section-copy-item-header">
                        <h5><strong>{section.section_name || `Section ${index + 1}`}</strong></h5>
                        <p><strong>Purpose:</strong> {section.communicates || 'N/A'}</p>
                        <p><strong>Structure:</strong> {section.text_structure || 'N/A'}</p>
                      </div>
                      <div className="section-copy-item-content">
                        {section.crop_image && (
                          <div className="compact-section-screenshot">
                            <img 
                              src={`${API_URL}/uploads/${section.crop_image}`} 
                              alt={`${section.section_name} screenshot`}
                              style={{ maxWidth: '200px', maxHeight: '120px', cursor: 'pointer' }}
                              onClick={() => handleImageClick(
                                `${API_URL}/uploads/${section.crop_image}`,
                                `${section.section_name} - ${section.communicates}`
                              )}
                            />
                          </div>
                        )}
                        <div className="copy-content">
                          {section.copy_options && section.copy_options.length > 0 ? (
                            <div className="copy-options">
                              {section.copy_options.map((option, optionIndex) => {
                                const confidenceClass = option.confidence >= 90 ? 'high-confidence' : 
                                                      option.confidence >= 80 ? 'medium-confidence' : 'low-confidence'
                                return (
                                  <div key={optionIndex} className={`copy-option ${confidenceClass}`}>
                                    <div className="option-header">
                                      <span className="option-number">Option {optionIndex + 1}</span>
                                      <span className="confidence-score">{option.confidence}% confidence</span>
                                    </div>
                                    <div className="option-text" dangerouslySetInnerHTML={{ __html: formatCopyText(option.generated_text) }} />
                                    <div className="option-justification">
                                      <strong>Why this converts:</strong> {option.justification}
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          ) : (
                            <div className="generated-copy">No copy options available</div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  const formatCopyText = (text: string) => {
    if (!text || text.trim() === '') {
      return '<p>No content available</p>'
    }
    
    const cleanText = text.trim()
    const paragraphs = cleanText.split(/\n\s*\n/)
    
    const formattedParagraphs = paragraphs
      .filter(p => p.trim())
      .map(paragraph => {
        const formattedParagraph = paragraph.trim().replace(/\n/g, '<br>')
        return `<p>${formattedParagraph}</p>`
      })
    
    return formattedParagraphs.join('')
  }

  const parseProductsFromText = (text: string) => {
    // Remove intro text first
    let cleanText = text
    
    // Find where the actual product content starts by looking for the first numbered product
    const firstProductMatch = text.match(/(\n|^)\s*1\.\s+[A-Za-z][^\n]*/g)
    
    if (firstProductMatch && firstProductMatch.length > 0) {
      // Find the position where products start
      const firstProductIndex = text.indexOf(firstProductMatch[0])
      if (firstProductIndex > 0) {
        // Remove everything before the first product
        cleanText = text.substring(firstProductIndex).trim()
      }
    }
    
    // Split by numbered products (1., 2., 3., etc.)
    const productMatches = cleanText.match(/\d+\.\s+[A-Za-z][^\n]*[\s\S]*?(?=\n\d+\.\s+[A-Za-z]|\n*$)/g)
    
    if (productMatches && productMatches.length > 0) {
      return productMatches.map((match, index) => {
        const trimmed = match.trim()
        const lines = trimmed.split('\n')
        
        // Extract product name from first line
        const firstLine = lines[0] || ''
        const nameMatch = firstLine.match(/^\d+\.\s+(.+)$/)
        const productName = nameMatch ? nameMatch[1].trim() : `Product ${index + 1}`
        
        // Get content after first line
        const content = lines.slice(1).join('\n').trim()
        
        return {
          name: productName,
          content: content
        }
      })
    }
    
    // Fallback: if no numbered products found, try to split by standalone product names
    const lines = text.split('\n')
    const products = []
    let currentProduct = null
    let currentContent = []
    let inProductSection = false
    
    for (const line of lines) {
      const trimmed = line.trim()
      
      // Skip intro lines
      if (trimmed.includes("Here's the conversion") || 
          trimmed.includes("optimized for clarity") ||
          trimmed.includes("emotional resonance") ||
          trimmed.match(/^#{1,6}/)) {
        continue
      }
      
      // Check if this looks like a product name
      const isProductName = trimmed.length > 0 && 
                           trimmed.length < 50 && 
                           !trimmed.includes(':') && 
                           !trimmed.includes('Claims') &&
                           !trimmed.includes('Key Benefits') &&
                           !trimmed.includes('Instructions') &&
                           !trimmed.includes('Volume') &&
                           !trimmed.includes('Why This Works') &&
                           trimmed.split(' ').length <= 4 &&
                           !trimmed.endsWith('.')
      
      if (isProductName && !inProductSection) {
        // Start of a new product
        if (currentProduct && currentContent.length > 0) {
          products.push({
            name: currentProduct,
            content: currentContent.join('\n').trim()
          })
        }
        currentProduct = trimmed
        currentContent = []
        inProductSection = true
      } else if (trimmed.length > 0 && inProductSection) {
        // Add content to current product
        currentContent.push(trimmed)
      }
    }
    
    // Add the last product
    if (currentProduct && currentContent.length > 0) {
      products.push({
        name: currentProduct,
        content: currentContent.join('\n').trim()
      })
    }
    
    // If we found products, return them
    if (products.length > 0) {
      return products
    }
    
    // Final fallback: return all text as one product
    return [{
      name: "Generated Copy",
      content: text
    }]
  }

  const renderMarkdown = (text: string) => {
    // Enhanced markdown rendering for product copy
    return text
      // Headers
      .replace(/### (.*?)$/gim, '<h3>$1</h3>')
      .replace(/## (.*?)$/gim, '<h2>$1</h2>')
      .replace(/# (.*?)$/gim, '<h1>$1</h1>')
      
      // Bold and italic
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Handle bullet points with better formatting
      .replace(/^\* (.*?)$/gim, '<li>$1</li>')
      
      // Wrap consecutive list items in ul tags
      .replace(/(<li>.*<\/li>)/g, (match) => {
        const items = match.split('</li>').filter(item => item.trim())
        if (items.length > 0) {
          return '<ul>' + items.map(item => item + '</li>').join('') + '</ul>'
        }
        return match
      })
      
      // Convert double line breaks to paragraphs
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.)/gm, '<p>$1') // Start with paragraph
      .replace(/(.)$/gm, '$1</p>') // End with paragraph
      
      // Clean up extra paragraph tags around other elements
      .replace(/<p>(<h[1-6]>)/g, '$1')
      .replace(/(<\/h[1-6]>)<\/p>/g, '$1')
      .replace(/<p>(<ul>)/g, '$1')
      .replace(/(<\/ul>)<\/p>/g, '$1')
      .replace(/<p>(<li>)/g, '$1')
      .replace(/(<\/li>)<\/p>/g, '$1')
      
      // Handle single line breaks within paragraphs
      .replace(/\n/g, '<br>')
      
      // Clean up empty paragraphs
      .replace(/<p><\/p>/g, '')
      .replace(/<p><br><\/p>/g, '')
  }

  return (
    <div className="container">
      {/* Header Section - Matching original Flask website */}
     {/*  <div className="header">
        <div className="header-content">
          <Image 
            src="/logo.png" 
            alt="Logo" 
            className="site-logo" 
            width={34} 
            height={34}
          />
          <h1><i className="fas fa-magic"></i> Ecom Copy Writer</h1>
          <div className="header-subtitle">
            AI-Powered Brand-Perfect Copy Generation
          </div>
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-number">10x</span>
              <span className="stat-label">Faster Copy</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">95%</span>
              <span className="stat-label">Brand Accuracy</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">3-Step</span>
              <span className="stat-label">AI Framework</span>
            </div>
          </div>
        </div>
      </div>
      */}
      
      <div className="main-content">
        <form onSubmit={handleSubmit}>
          <div className="content-grid">
            {/* Left Column - Form Controls */}
            <div className="left-column">
              <div className="column-header">
                <h2>Copy Writer Agent</h2>
              </div>

              {/* Brand Selection */}
              <div className="form-group">
                <label>
                  <i className="fas fa-tag"></i>
                  Brand Selection
                </label>
                
                <div className="brand-type-selection">
                  <label className="radio-option">
                    <input 
                      type="radio" 
                      name="brand_type" 
                      value="existing" 
                      checked={brandType === 'existing'}
                      onChange={() => setBrandType('existing')}
                    />
                    <span className="radio-label">Select from existing brands</span>
                  </label>
                  <label className="radio-option">
                    <input 
                      type="radio" 
                      name="brand_type" 
                      value="custom"
                      checked={brandType === 'custom'}
                      onChange={() => setBrandType('custom')}
                    />
                    <span className="radio-label">Enter custom client name</span>
                  </label>
                </div>

                {brandType === 'existing' ? (
                  <select 
                    value={selectedBrand} 
                    onChange={(e) => setSelectedBrand(e.target.value)}
                    required={brandType === 'existing'}
                  >
                    <option value="">Choose your brand...</option>
                    {brands.map(brand => (
                      <option key={brand} value={brand}>{brand}</option>
                    ))}
                  </select>
                ) : (
                  <div>
                    <input 
                      type="text" 
                      value={customBrand}
                      onChange={(e) => setCustomBrand(e.target.value)}
                      placeholder="Enter your client/brand name..." 
                      required={brandType === 'custom'}
                    />
                    <small style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem', display: 'block' }}>
                      💡 Custom clients won't have pre-loaded brand guidelines, but you can provide context below
                    </small>
                  </div>
                )}
              </div>

              {/* Additional Context */}
              <div className="form-group">
                <label htmlFor="additionalContext">
                  <i className="fas fa-comment-dots"></i>
                  Additional Instructions (Optional)
                </label>
                <textarea 
                  id="additionalContext"
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  placeholder="Add any specific details about your target audience, campaign goals, special offers, or unique selling points..." 
                  rows={6}
                />
              </div>

              {/* Action Section */}
              <div className="action-section">
                <button type="submit" className="generate-btn" disabled={loading}>
                  {loading ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i> Processing...
                    </>
                  ) : (
                    <>
                      <i className={uploadType === 'image' ? "fas fa-search" : "fas fa-file-text"}></i> 
                      {uploadType === 'image' ? ' Analyze Design' : ' Process Document'}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Right Column - Upload Section */}
            <div className="right-column">
              {/* Upload Type Selection */}
              <div className="upload-type-selection">
                <label className="radio-option">
                  <input 
                    type="radio" 
                    name="upload_type" 
                    value="image"
                    checked={uploadType === 'image'}
                    onChange={() => setUploadType('image')}
                  />
                  <span className="radio-label">
                    <i className="fas fa-image"></i>
                    Upload Screenshot
                  </span>
                </label>
                <label className="radio-option">
                  <input 
                    type="radio" 
                    name="upload_type" 
                    value="docs"
                    checked={uploadType === 'docs'}
                    onChange={() => setUploadType('docs')}
                  />
                  <span className="radio-label">
                    <i className="fas fa-file-alt"></i>
                    Upload Document
                  </span>
                </label>
              </div>

              {/* Image Upload Section */}
              {uploadType === 'image' && (
                <div 
                  className="upload-section"
                  onClick={() => imageInputRef.current?.click()}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, 'image')}
                >
                  {!uploadedImage && (
                    <div className="upload-icon">
                      <i className="fas fa-cloud-upload-alt"></i>
                    </div>
                  )}
                  <div className="upload-text">
                    {uploadedImage ? uploadedImage.name : 'Drop your design screenshot here'}
                  </div>
                  <div className="upload-subtext">
                    {uploadedImage ? 'Click to change image' : 'or click to browse and select your file'}
                  </div>
                  {!uploadedImage && (
                    <div className="upload-features">
                      <div className="upload-feature">
                        <i className="fas fa-check-circle"></i>
                        <span>PNG, JPG, WEBP</span>
                      </div>
                      <div className="upload-feature">
                        <i className="fas fa-weight-hanging"></i>
                        <span>Up to 16MB</span>
                      </div>
                      <div className="upload-feature">
                        <i className="fas fa-zap"></i>
                        <span>AI Analysis</span>
                      </div>
                    </div>
                  )}
                  <input 
                    ref={imageInputRef}
                    type="file" 
                    accept="image/*" 
                    style={{ display: 'none' }}
                    onChange={handleImageUpload}
                  />
                  {previewImage && (
                    <img 
                      src={previewImage} 
                      alt="Preview" 
                      className="preview-image"
                    />
                  )}
                </div>
              )}

              {/* Google Docs Upload Section */}
              {uploadType === 'docs' && (
                <div 
                  className="upload-section"
                  onClick={() => docsInputRef.current?.click()}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, 'docs')}
                >
                  <div className="upload-icon">
                    <i className="fas fa-file-alt"></i>
                  </div>
                  <div className="upload-text">
                    {uploadedDocs ? uploadedDocs.name : 'Upload your Google Docs file'}
                  </div>
                  <div className="upload-subtext">
                    {uploadedDocs ? 'Click to change document':'or click to browse and select your file'}
                  </div>
                  
                  
                  
                  {!uploadedDocs  && (
                    <div className="upload-features">
                      
                      <div className="upload-feature">
                        <i className="fas fa-file-upload"></i>
                        <span>DOCX Files</span>
                      </div>
                      <div className="upload-feature">
                        <i className="fas fa-brain"></i>
                        <span>Text Extraction</span>
                      </div>
                    </div>
                  )}
                  
                  <input 
                    ref={docsInputRef}
                    type="file" 
                    accept=".docx,.doc,.pdf,.txt" 
                    style={{ display: 'none' }}
                    onChange={handleDocsUpload}
                  />
                </div>
              )}
            </div>



            {/* Loading State */}
            {loading && (
              <div ref={loadingRef} className="loading" style={{ display: 'block' }}>
                <div className="spinner"></div>
                <h3>
                  {uploadType === 'image' ? 'Analyzing your design...' : 'Processing your document...'}
                </h3>
                <p>Our AI is identifying sections and preparing copy generation</p>
              </div>
            )}
          </div>
        </form>

        {/* Analysis Confirmation */}
        {showConfirmation && (
          <div ref={confirmationRef} className="confirmation">
            <div className="confirmation-content">
              <div className="analysis-summary">
                <div className="summary-header">
                  <h3>
                    <i className="fas fa-search"></i>
                    Analysis Complete
                  </h3>
                  <p>Detected {sections.length} sections • Review and confirm before generating copy</p>
                </div>
              </div>
              
              <div className="sections-grid">
                {sections.map((section, index) => (
                  <div key={index} className="section-analysis">
                    <div className="analysis-header">
                      <div className="section-info">
                        <div className="section-id">
                          <i className="fas fa-layer-group"></i>
                          {section.id}
                        </div>
                        <div className="section-location">{section.location}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                        <div className="section-type-badge">{section.type}</div>
                        <div className="section-actions">
                          <button 
                            className="section-action-btn"
                            onClick={() => openSectionEditor(section, false)}
                            title="Edit section"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button 
                            className="section-action-btn delete-btn"
                            onClick={() => handleSectionDelete(section.id)}
                            title="Delete section"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                    {section.crop_image && (
                      <div className="section-screenshot">
                        <img 
                          src={`${API_URL}/uploads/${section.crop_image}`} 
                          alt={`${section.id} screenshot`}
                          onClick={() => handleImageClick(
                            `${API_URL}/uploads/${section.crop_image}`,
                            `${section.id} - ${section.location} (${section.type})`
                          )}
                        />
                        <div className="section-screenshot-label">
                          <i className="fas fa-expand"></i>
                          Click to view full size
                        </div>
                      </div>
                    )}
                    <div className="analysis-details">
                      <div className="analysis-row">
                        <div className="analysis-label">
                          <i className="fas fa-bullseye"></i>
                          Purpose
                        </div>
                        <div className="analysis-value purpose-value">{section.purpose}</div>
                      </div>
                      
                      <div className="analysis-row">
                        <div className="analysis-label">
                          <i className="fas fa-list"></i>
                          Structure
                        </div>
                        <div className="analysis-value structure-value">{section.text_structure}</div>
                      </div>
                      
                      <div className="analysis-row">
                        <div className="analysis-label">
                          <i className="fas fa-font"></i>
                          Current Text
                        </div>
                        <div className="analysis-value current-text-value">
                          {section.current_text || 'No text detected'}
                        </div>
                      </div>
                    </div>
                    
                  
                  </div>
                ))}
              </div>
            </div>
            
            <div className="confirmation-actions">
              <div className="action-buttons-group">
                <button 
                  type="button" 
                  className="add-section-btn"
                  onClick={() => openSectionEditor(undefined, true)}
                >
                  <i className="fas fa-plus"></i> Add New Section
                </button>
                <button 
                  type="button" 
                  className="secondary-btn"
                  onClick={() => {
                    setShowConfirmation(false)
                    setSections([])
                  }}
                >
                  <i className="fas fa-arrow-left"></i> Back to Upload
                </button>
              </div>
              <button 
                type="button" 
                className="confirm-btn"
                onClick={confirmAnalysis}
                disabled={loading}
              >
                <i className="fas fa-wand-magic-sparkles"></i> Generate Brand-Perfect Copy
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {renderResults()}
      </div>

            {/* Snackbar for notifications */}
      <Snackbar
        message={snackbar.message}
        type={snackbar.type}
        isVisible={snackbar.isVisible}
        onClose={hideSnackbar}
        duration={5000}
      />

      {/* Lightbox for image viewing */}
      <Lightbox
        isOpen={lightboxImage !== null}
        imageSrc={lightboxImage?.src || ''}
        imageAlt={lightboxImage?.alt || ''}
        onClose={closeLightbox}
      />

      {/* Section Editor */}
      <SectionEditor
        section={sectionEditor.section}
        isOpen={sectionEditor.isOpen}
        onClose={closeSectionEditor}
        onSave={handleSectionSave}
        isNewSection={sectionEditor.isNew}
      />
    </div>
  )
} 