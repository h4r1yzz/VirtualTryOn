"use client"

import type React from "react"

import { useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Upload, User, Shirt, Sparkles, ImageIcon, Trash2, AlertCircle } from "lucide-react"
import { useFashionStore, UploadedImage } from "@/lib/stores"
import { FashionAPI, validateImageFile, handleAPIError } from "@/lib/api"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
import ProductCard from "@/components/ProductCard"

export default function VirtualWardrobePage() {
  const {
    userImage,
    apparelItems,
    selectedApparel,
    isAnalyzing,
    isGenerating,
    analysisResult,
    generationResult,
    error,
    setUserImage,
    addApparelItem,
    removeApparelItem,
    setSelectedApparel,
    setAnalyzing,
    setGenerating,
    setAnalysisResult,
    setGenerationResult,
    setError,
    clearResults
  } = useFashionStore()

  const userFileInputRef = useRef<HTMLInputElement>(null)
  const apparelFileInputRef = useRef<HTMLInputElement>(null)

  // Debug logging to help identify state issues
  console.log('Debug State:', {
    hasUserImage: !!userImage,
    hasSelectedApparel: !!selectedApparel,
    apparelItemsCount: apparelItems.length,
    selectedApparelId: selectedApparel?.id
  })

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>, type: "user" | "apparel") => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!validateImageFile(file)) {
      setError("Invalid file type. Please upload JPEG, PNG, or WebP images only.")
      return
    }

    // Clear any previous errors
    setError(null)

    const url = URL.createObjectURL(file)
    const newImage: UploadedImage = {
      id: Date.now().toString(),
      url,
      name: file.name,
      type,
      file // Store the actual file for API calls
    }

    if (type === "user") {
      setUserImage(newImage)
    } else {
      addApparelItem(newImage)
      // Auto-select the newly uploaded apparel item
      setSelectedApparel(newImage)
    }

    // Reset the input
    event.target.value = ''
  }



  const handleGenerateProduct = async () => {
    if (!userImage?.file || !selectedApparel?.file) {
      setError("Please upload both a user image and select a clothing item")
      return
    }

    setGenerating(true)
    setError(null)
    clearResults()

    try {
      const result = await FashionAPI.generateProductImages(
        selectedApparel.file,
        userImage.file,
        `product_${Date.now()}`
      )
      console.log('Setting generation result:', result)
      console.log('Generated images in result:', result.generated_images)
      setGenerationResult(result)
    } catch (error) {
      console.error('Generation error:', error)
      setError(handleAPIError(error))
    } finally {
      setGenerating(false)
    }
  }

  const removeImage = (id: string, type: "user" | "apparel") => {
    if (type === "user") {
      setUserImage(null)
    } else {
      removeApparelItem(id)
    }
  }

  const handleViewImage = (imagePath: string) => {
    // Open the image in a new tab for viewing
    const fullImageUrl = `${API_BASE_URL}${imagePath}`
    window.open(fullImageUrl, '_blank')
  }

  const handleDownloadImage = async (imagePath: string) => {
    try {
      // Construct the full image URL
      const fullImageUrl = `${API_BASE_URL}${imagePath}`

      // Fetch the image as a blob
      const response = await fetch(fullImageUrl)
      if (!response.ok) {
        throw new Error('Failed to fetch image')
      }

      const blob = await response.blob()

      // Create a download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // Extract filename from path or create a default one
      const filename = imagePath.split('/').pop() || 'generated-image.png'
      link.download = filename

      // Trigger download
      document.body.appendChild(link)
      link.click()

      // Cleanup
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download image:', error)
      setError('Failed to download image. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Sparkles className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">Virtual Wardrobe</h1>
                <p className="text-sm text-muted-foreground">AI-Powered Outfit Try-On</p>
              </div>
            </div>
            <Badge variant="secondary" className="text-xs">
              Beta
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Left Panel - Upload & Controls */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Your Photo
                </CardTitle>
                <CardDescription>Upload a clear photo of yourself for the best try-on results</CardDescription>
              </CardHeader>
              <CardContent>
                {userImage ? (
                  <div className="space-y-4">
                    <div className="relative aspect-[3/4] overflow-hidden rounded-lg border border-border">
                      <img
                        src={userImage.url || "/placeholder.svg"}
                        alt="User"
                        className="h-full w-full object-cover"
                      />
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setUserImage(null)} className="w-full">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Remove Photo
                    </Button>
                  </div>
                ) : (
                  <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/50 p-8 text-center hover:bg-muted/80 transition-colors">
                    <Upload className="mb-4 h-8 w-8 text-muted-foreground" />
                    <p className="text-sm font-medium text-foreground">Upload your photo</p>
                    <p className="text-xs text-muted-foreground">PNG, JPG up to 10MB</p>
                    <input
                      ref={userFileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageUpload(e, "user")}
                      className="hidden"
                    />
                  </label>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shirt className="h-5 w-5" />
                  Add Apparel
                </CardTitle>
                <CardDescription>Upload clothing items to try on</CardDescription>
              </CardHeader>
              <CardContent>
                <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/50 p-6 text-center hover:bg-muted/80 transition-colors">
                  <ImageIcon className="mb-2 h-6 w-6 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">Add clothing item</p>
                  <p className="text-xs text-muted-foreground">PNG, JPG up to 10MB</p>
                  <input
                    ref={apparelFileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload(e, "apparel")}
                    className="hidden"
                  />
                </label>
              </CardContent>
            </Card>

            {/* Error Display */}
            {error && (
              <Card className="border-destructive">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 text-destructive">
                    <AlertCircle className="h-4 w-4" />
                    <p className="text-sm">{error}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Status Indicator */}
            <Card className="bg-muted/50">
              <CardContent className="pt-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${userImage ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className="text-sm">User photo {userImage ? '✓' : '(required)'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${selectedApparel ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className="text-sm">Clothing selected {selectedApparel ? '✓' : '(click to select)'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="space-y-3">
              {userImage && selectedApparel && (
                <Button
                  onClick={handleGenerateProduct}
                  disabled={isGenerating}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <ImageIcon className="mr-2 h-4 w-4" />
                      Generate Product Images
                    </>
                  )}
                </Button>
              )}

              {/* Help text when conditions not met */}
              {!selectedApparel && apparelItems.length > 0 && (
                <Card className="border-amber-200 bg-amber-50">
                  <CardContent className="pt-4">
                    <p className="text-sm text-amber-800">
                      👆 Click on a clothing item above to select it
                    </p>
                  </CardContent>
                </Card>
              )}

              {!userImage && (
                <Card className="border-blue-200 bg-blue-50">
                  <CardContent className="pt-4">
                    <p className="text-sm text-blue-800">
                      📸 Upload your photo to generate product images
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* Center Panel - Apparel Gallery */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Your Wardrobe</CardTitle>
                <CardDescription>Select an item to try on</CardDescription>
              </CardHeader>
              <CardContent>
                {apparelItems.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Shirt className="mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-sm font-medium text-foreground">No items yet</p>
                    <p className="text-xs text-muted-foreground">Upload some clothing to get started</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {apparelItems.map((item) => (
                      <div
                        key={item.id}
                        className={`group relative cursor-pointer overflow-hidden rounded-lg border-2 transition-all ${
                          selectedApparel?.id === item.id
                            ? "border-primary ring-2 ring-primary/20"
                            : "border-border hover:border-primary/50"
                        }`}
                        onClick={() => setSelectedApparel(item)}
                      >
                        <div className="aspect-square">
                          <img
                            src={item.url || "/placeholder.svg"}
                            alt={item.name}
                            className="h-full w-full object-cover"
                          />
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            removeApparelItem(item.id)
                          }}
                          className="absolute right-2 top-2 rounded-full bg-destructive p-1 opacity-0 transition-opacity group-hover:opacity-100"
                        >
                          <Trash2 className="h-3 w-3 text-destructive-foreground" />
                        </button>
                        {selectedApparel?.id === item.id && (
                          <div className="absolute inset-0 flex items-center justify-center bg-primary/20">
                            <Badge variant="default" className="text-xs">
                              Selected
                            </Badge>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Results */}
          <div className="space-y-6">
            {!analysisResult && !generationResult ? (
              <Card>
                <CardHeader>
                  <CardTitle>AI Analysis Results</CardTitle>
                  <CardDescription>Generate product images to see AI insights and results</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex aspect-[3/4] flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/50 text-center">
                    <Sparkles className="mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-sm font-medium text-foreground">No results yet</p>
                    <p className="text-xs text-muted-foreground">Upload photos and generate product images to get started</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <ProductCard
                analysis={analysisResult?.analysis || generationResult?.analysis!}
                generatedImages={generationResult?.generated_images || []}
                onViewImage={handleViewImage}
                onDownloadImage={handleDownloadImage}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
