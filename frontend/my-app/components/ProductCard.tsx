import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Shirt, 
  Palette, 
  Scissors, 
  Sun, 
  Download, 
  Eye,
  Sparkles,
  Tag
} from "lucide-react"
import { ClothingAnalysis } from "@/lib/stores"

interface ProductCardProps {
  analysis: ClothingAnalysis
  generatedImages?: string[]
  onDownloadImage?: (imagePath: string) => void
  onViewImage?: (imagePath: string) => void
}

export const ProductCard: React.FC<ProductCardProps> = ({
  analysis,
  generatedImages = [],
  onDownloadImage,
  onViewImage
}) => {
  // Debug logging
  console.log('ProductCard received generatedImages:', generatedImages)
  console.log('ProductCard generatedImages length:', generatedImages.length)

  const getSeasonIcon = (season: string) => {
    switch (season.toLowerCase()) {
      case 'summer':
        return '☀️'
      case 'winter':
        return '❄️'
      case 'spring':
        return '🌸'
      case 'fall':
      case 'autumn':
        return '🍂'
      default:
        return '🌤️'
    }
  }

  const getStyleColor = (style: string) => {
    switch (style.toLowerCase()) {
      case 'formal':
        return 'bg-blue-100 text-blue-800'
      case 'casual':
        return 'bg-green-100 text-green-800'
      case 'vintage':
        return 'bg-purple-100 text-purple-800'
      case 'modern':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Analysis Results Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Analysis Results
          </CardTitle>
          <CardDescription>
            Detailed analysis of your clothing item
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Description */}
          <div>
            <h4 className="font-medium text-sm text-muted-foreground mb-2">Description</h4>
            <p className="text-sm leading-relaxed">{analysis.description}</p>
          </div>

          {/* Key Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Shirt className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Type</span>
              </div>
              <Badge variant="outline" className="capitalize">
                {analysis.clothing_type}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Palette className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Color</span>
              </div>
              <Badge variant="outline" className="capitalize">
                {analysis.color}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Scissors className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Material</span>
              </div>
              <Badge variant="outline" className="capitalize">
                {analysis.material}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Sun className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Season</span>
              </div>
              <Badge variant="outline" className="capitalize">
                {getSeasonIcon(analysis.season)} {analysis.season}
              </Badge>
            </div>
          </div>

          {/* Style and Texture */}
          <div className="space-y-3">
            <div>
              <span className="text-sm font-medium text-muted-foreground">Style: </span>
              <Badge className={`capitalize ${getStyleColor(analysis.style)}`}>
                {analysis.style}
              </Badge>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">Texture: </span>
              <span className="text-sm capitalize">{analysis.texture}</span>
            </div>
          </div>

          {/* Tags */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Tag className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Tags</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {analysis.tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Generated Images Card */}
      {generatedImages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-primary" />
              Generated Product Images
            </CardTitle>
            <CardDescription>
              AI-generated product listing images ({generatedImages.length} images)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {generatedImages.map((imagePath, index) => (
                <div key={index} className="space-y-2">
                  <div className="aspect-square bg-muted rounded-lg overflow-hidden">
                    <img
                      src={`http://localhost:8000${imagePath}`}
                      alt={`Generated product view ${index + 1}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        console.error('Failed to load image:', imagePath)
                        e.currentTarget.style.display = 'none'
                        e.currentTarget.nextElementSibling?.classList.remove('hidden')
                      }}
                    />
                    <div className="hidden w-full h-full flex items-center justify-center">
                      <span className="text-sm text-muted-foreground">
                        Failed to load image
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {onViewImage && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onViewImage(imagePath)}
                        className="flex-1"
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    )}
                    {onDownloadImage && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDownloadImage(imagePath)}
                        className="flex-1"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ProductCard
