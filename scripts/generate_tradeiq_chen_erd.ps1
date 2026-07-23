Add-Type -AssemblyName System.Drawing

$outDir = Join-Path $PSScriptRoot "..\docs"
$outPath = Join-Path $outDir "tradeiq-chen-erd.png"

$width = 2600
$height = 1900

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::White)

$entityPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(70, 80, 110), 2.5)
$relPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(85, 85, 85), 2.2)
$attrPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(110, 110, 110), 1.7)
$entityFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(242, 246, 255))
$relFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(238, 238, 238))
$attrFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 255))
$titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(22, 40, 72))
$textBrush = [System.Drawing.Brushes]::Black
$mutedBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(95, 95, 95))

$titleFont = New-Object System.Drawing.Font("Arial", 24, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Regular)
$entityFont = New-Object System.Drawing.Font("Arial", 15, [System.Drawing.FontStyle]::Bold)
$attrFont = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Regular)
$cardFont = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)

function CenterText {
    param(
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [int]$X,
        [int]$Y,
        [int]$W,
        [int]$H
    )
    $size = $graphics.MeasureString($Text, $Font)
    $tx = $X + (($W - $size.Width) / 2)
    $ty = $Y + (($H - $size.Height) / 2) - 1
    $graphics.DrawString($Text, $Font, $Brush, $tx, $ty)
}

function DrawEntity {
    param([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Name)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $graphics.FillRectangle($entityFill, $rect)
    $graphics.DrawRectangle($entityPen, $rect)
    CenterText $Name $entityFont $titleBrush $X $Y $W $H
}

function DrawRelationship {
    param([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Name)
    $points = [System.Drawing.Point[]]@(
        (New-Object System.Drawing.Point([int]($X + ($W / 2)), $Y)),
        (New-Object System.Drawing.Point([int]($X + $W), [int]($Y + ($H / 2)))),
        (New-Object System.Drawing.Point([int]($X + ($W / 2)), [int]($Y + $H))),
        (New-Object System.Drawing.Point($X, [int]($Y + ($H / 2))))
    )
    $graphics.FillPolygon($relFill, $points)
    $graphics.DrawPolygon($relPen, $points)
    CenterText $Name $cardFont $titleBrush $X $Y $W $H
}

function DrawAttribute {
    param([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Name,[bool]$Key = $false)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $graphics.FillEllipse($attrFill, $rect)
    $graphics.DrawEllipse($attrPen, $rect)
    $font = if ($Key) { $cardFont } else { $attrFont }
    $brush = if ($Key) { $titleBrush } else { $textBrush }
    CenterText $Name $font $brush $X $Y $W $H
}

function DrawLine {
    param([int]$X1,[int]$Y1,[int]$X2,[int]$Y2)
    $graphics.DrawLine($relPen, $X1, $Y1, $X2, $Y2)
}

function Cardinality {
    param([int]$X,[int]$Y,[string]$Text)
    $graphics.DrawString($Text, $cardFont, $titleBrush, $X, $Y)
}

function RelationLabel {
    param([int]$X,[int]$Y,[string]$Text)
    $graphics.DrawString($Text, $smallFont, $mutedBrush, $X, $Y)
}

$graphics.DrawString("TradeIQ Chen-Style ER Diagram", $titleFont, $titleBrush, 840, 20)
$graphics.DrawString("Current database entities from backend/app/models.py", $subtitleFont, $mutedBrush, 900, 58)

# Entities
DrawEntity 1020 130 560 120 "USERS"
DrawEntity 80 430 470 140 "PORTFOLIO_SETUP"
DrawEntity 650 430 500 170 "TRADE_LOG"
DrawEntity 1270 430 450 150 "HOLDINGS"
DrawEntity 1880 430 420 140 "RISK_METRICS"
DrawEntity 180 870 500 150 "INVESTMENT_THESIS"
DrawEntity 780 870 520 150 "THESIS_SCORES"
DrawEntity 1440 870 560 160 "WEEKLY_SCORES"
DrawEntity 910 1310 470 130 "LEADERBOARD"
DrawEntity 1470 1310 420 120 "REPORTS"

# Relationships
DrawRelationship 560 610 180 90 "HAS_PORTFOLIO"
DrawRelationship 860 620 160 90 "MAKES"
DrawRelationship 1440 620 150 90 "OWNS"
DrawRelationship 2030 610 150 90 "HAS_RISK"
DrawRelationship 560 950 170 90 "WRITES"
DrawRelationship 1040 960 170 90 "SCORED_BY"
DrawRelationship 1680 990 180 90 "GETS_SCORE"
DrawRelationship 1150 1425 180 90 "RANKS_IN"
DrawRelationship 1690 1425 170 90 "GENERATES"

# Attributes for USERS
DrawAttribute 920 60 130 48 "user_id" $true
DrawAttribute 880 80 160 50 "full_name"
DrawAttribute 1110 80 120 50 "email"
DrawAttribute 1240 80 160 50 "university"
DrawAttribute 1410 80 120 50 "role"
DrawAttribute 1535 80 150 50 "password_hash"

# Attributes for PORTFOLIO_SETUP
DrawAttribute 20 350 140 46 "portfolio_id" $true
DrawAttribute 70 560 120 46 "total_capital"
DrawAttribute 205 560 110 46 "cash_balance"
DrawAttribute 330 560 120 46 "risk_appetite"
DrawAttribute 460 560 120 46 "investment_horizon"
DrawAttribute 320 365 120 46 "user_id"

# Attributes for TRADE_LOG
DrawAttribute 615 340 120 46 "trade_id" $true
DrawAttribute 560 355 130 46 "trade_date"
DrawAttribute 800 355 140 46 "stock_ticker"
DrawAttribute 960 355 140 46 "stock_name"
DrawAttribute 1110 355 100 46 "sector"
DrawAttribute 700 560 160 46 "allocation_percent"
DrawAttribute 875 560 150 46 "amount_invested"
DrawAttribute 1035 560 110 46 "quantity"
DrawAttribute 1160 560 110 46 "buy_price"
DrawAttribute 1285 560 150 46 "current_sell_price"
DrawAttribute 1450 560 120 46 "trade_type"
DrawAttribute 1575 560 95 46 "tag1"
DrawAttribute 1675 560 95 46 "tag2"
DrawAttribute 1775 560 95 46 "tag3"
DrawAttribute 1875 560 105 46 "thesis"

# Attributes for HOLDINGS
DrawAttribute 1260 350 120 46 "holding_id" $true
DrawAttribute 1230 560 120 46 "stock_ticker"
DrawAttribute 1360 560 120 46 "stock_name"
DrawAttribute 1490 560 120 46 "quantity"
DrawAttribute 1620 560 130 46 "avg_buy_price"
DrawAttribute 1760 560 120 46 "current_price"
DrawAttribute 1890 560 130 46 "market_value"
DrawAttribute 2030 560 120 46 "profit_loss"

# Attributes for RISK_METRICS
DrawAttribute 1880 340 100 46 "risk_id" $true
DrawAttribute 1840 560 130 46 "sharpe_ratio"
DrawAttribute 1980 560 90 46 "beta"
DrawAttribute 2080 560 120 46 "volatility"
DrawAttribute 2210 560 150 46 "max_drawdown"
DrawAttribute 2370 560 100 46 "var_value"

# Attributes for INVESTMENT_THESIS
DrawAttribute 120 790 110 46 "thesis_id" $true
DrawAttribute 30 1030 140 46 "trade_id"
DrawAttribute 190 1030 120 46 "investment_style"
DrawAttribute 325 1030 100 46 "risk_level"
DrawAttribute 435 1030 145 46 "confidence_score"
DrawAttribute 260 780 120 46 "reason_text"

# Attributes for THESIS_SCORES
DrawAttribute 760 790 100 46 "score_id" $true
DrawAttribute 700 1030 130 46 "clarity_score"
DrawAttribute 835 1030 145 46 "reasoning_score"
DrawAttribute 985 1030 160 46 "risk_awareness_score"
DrawAttribute 1150 1030 170 46 "market_understanding_score"
DrawAttribute 890 780 100 46 "total_score"
DrawAttribute 1040 780 100 46 "feedback"

# Attributes for WEEKLY_SCORES
DrawAttribute 1390 790 100 46 "score_id" $true
DrawAttribute 1330 1040 120 46 "week_number"
DrawAttribute 1465 1040 135 46 "portfolio_score"
DrawAttribute 1610 1040 100 46 "risk_score"
DrawAttribute 1715 1040 110 46 "thesis_score"
DrawAttribute 1830 1040 140 46 "execution_score"
DrawAttribute 1975 1040 130 46 "strategy_score"
DrawAttribute 2115 1040 120 46 "final_score"
DrawAttribute 2245 1040 120 46 "rank_position"

# Attributes for LEADERBOARD
DrawAttribute 865 1205 120 46 "leaderboard_id" $true
DrawAttribute 820 1495 120 46 "week_number"
DrawAttribute 955 1495 110 46 "final_score"
DrawAttribute 1080 1495 110 46 "rank_position"

# Attributes for REPORTS
DrawAttribute 1480 1205 100 46 "report_id" $true
DrawAttribute 1460 1495 120 46 "week_number"
DrawAttribute 1590 1495 120 46 "report_path"
DrawAttribute 1720 1495 120 46 "generated_at"

# Entity to relationship connectors - USERS
DrawLine 1300 250 650 610
Cardinality 770 380 "1"
Cardinality 1130 360 "1"

DrawLine 1200 250 940 620
Cardinality 950 360 "1"
Cardinality 840 380 "M"
RelationLabel 870 645 "users -> trades"

DrawLine 1460 250 1500 620
Cardinality 1520 360 "1"
Cardinality 1440 380 "M"
RelationLabel 1420 645 "users -> holdings"

DrawLine 1540 250 2030 610
Cardinality 1640 360 "1"
Cardinality 2000 360 "1"

DrawLine 1120 250 620 960
Cardinality 760 470 "M"
Cardinality 930 500 "1"
RelationLabel 300 780 "trade -> thesis"

DrawLine 1250 250 1100 960
Cardinality 1160 470 "1"
Cardinality 1030 500 "1"
RelationLabel 980 790 "thesis -> score"

DrawLine 1420 250 1730 990
Cardinality 1580 520 "1"
Cardinality 1760 550 "M"
RelationLabel 1630 920 "users -> weekly_scores"

DrawLine 1210 250 1120 1425
Cardinality 1180 650 "1"
Cardinality 1160 1310 "M"
RelationLabel 1130 1260 "users -> leaderboard"

DrawLine 1370 250 1760 1425
Cardinality 1490 650 "1"
Cardinality 1760 1320 "M"
RelationLabel 1600 1270 "users -> reports"

DrawLine 1090 250 320 610
Cardinality 540 360 "1"
Cardinality 170 360 "1"
RelationLabel 180 580 "user -> portfolio"

# Additional entity-specific relationship lines
DrawLine 400 520 650 520
DrawLine 1040 520 1270 520
DrawLine 1720 520 1880 520
DrawLine 430 890 580 890
DrawLine 1020 890 1440 890
DrawLine 1710 1365 1470 1365

# Notes
$graphics.DrawString("Chen notation: rectangles = entities, ovals = attributes, diamonds = relationships.", $smallFont, $mutedBrush, 760, 1760)

$bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Host "Saved $outPath"
