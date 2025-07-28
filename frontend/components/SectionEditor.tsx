'use client'

import React, { useState } from 'react'

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

interface SectionEditorProps {
  section?: Section
  isOpen: boolean
  onClose: () => void
  onSave: (section: Section) => void
  isNewSection?: boolean
}

const SectionEditor: React.FC<SectionEditorProps> = ({
  section,
  isOpen,
  onClose,
  onSave,
  isNewSection = false
}) => {
  const [editedSection, setEditedSection] = useState<Section>(
    section || {
      id: `section_${Date.now()}`,
      type: 'content',
      purpose: '',
      text_structure: '',
      location: '',
      current_text: ''
    }
  )

  const handleInputChange = (field: keyof Section, value: string) => {
    setEditedSection(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSave = () => {
    onSave(editedSection)
    onClose()
  }

  const handleCancel = () => {
    if (section) {
      setEditedSection(section)
    }
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="section-editor-overlay" onClick={onClose}>
      <div className="section-editor-modal" onClick={(e) => e.stopPropagation()}>
        <div className="section-editor-header">
          <h3>
            <i className={isNewSection ? "fas fa-plus" : "fas fa-edit"}></i>
            {isNewSection ? 'Add New Section' : 'Edit Section'}
          </h3>
          <button className="section-editor-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="section-editor-content">
          <div className="editor-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="section-id">
                  <i className="fas fa-tag"></i>
                  Section ID
                </label>
                <input
                  id="section-id"
                  type="text"
                  value={editedSection.id}
                  onChange={(e) => handleInputChange('id', e.target.value)}
                  placeholder="e.g., section_1, header, hero"
                />
              </div>

              <div className="form-group">
                <label htmlFor="section-location">
                  <i className="fas fa-map-marker-alt"></i>
                  Location
                </label>
                <input
                  id="section-location"
                  type="text"
                  value={editedSection.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="e.g., Top left corner, Below hero image"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="section-type">
                  <i className="fas fa-layer-group"></i>
                  Section Type
                </label>
                <select
                  id="section-type"
                  value={editedSection.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                >
                  <option value="hero">Hero</option>
                  <option value="navigation">Navigation</option>
                  <option value="content">Content</option>
                  <option value="product">Product</option>
                  <option value="cta">Call to Action</option>
                  <option value="footer">Footer</option>
                  <option value="sidebar">Sidebar</option>
                  <option value="banner">Banner</option>
                  <option value="testimonial">Testimonial</option>
                  <option value="feature">Feature</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="section-structure">
                  <i className="fas fa-list"></i>
                  Text Structure
                </label>
                <input
                  id="section-structure"
                  type="text"
                  value={editedSection.text_structure}
                  onChange={(e) => handleInputChange('text_structure', e.target.value)}
                  placeholder="e.g., Headline + subtext, Button text, List items"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="section-purpose">
                <i className="fas fa-bullseye"></i>
                Purpose
              </label>
              <textarea
                id="section-purpose"
                value={editedSection.purpose}
                onChange={(e) => handleInputChange('purpose', e.target.value)}
                placeholder="Describe what this section is meant to accomplish..."
                rows={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="section-text">
                <i className="fas fa-font"></i>
                Current Text
              </label>
              <textarea
                id="section-text"
                value={editedSection.current_text}
                onChange={(e) => handleInputChange('current_text', e.target.value)}
                placeholder="Enter the current text content of this section..."
                rows={4}
              />
            </div>
          </div>
        </div>

        <div className="section-editor-actions">
          <button className="editor-btn cancel-btn" onClick={handleCancel}>
            <i className="fas fa-times"></i>
            Cancel
          </button>
          <button className="editor-btn save-btn" onClick={handleSave}>
            <i className="fas fa-save"></i>
            {isNewSection ? 'Add Section' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SectionEditor 