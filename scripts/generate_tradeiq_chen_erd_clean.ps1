Add-Type -AssemblyName System.Drawing

$outDir = Join-Path $PSScriptRoot "..\docs"
$outPath = Join-Path $outDir "tradeiq-chen-erd-clean.png"

$width = 2400
$height = 1700

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::White)

$entityPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(65, 80, 110), 2.5)
$relPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(95, 95, 95), 2.0)
$attrPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(110, 110, 110), 1.5)
$entityFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(242, 246, 255))
$relFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(236, 236, 236))
$attrFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 255))
$titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(22, 40, 72))
$mutedBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(96, 96, 96))
$textBrush = [System.Drawing.Brushes]::Black

$titleFont = New-Object System.Drawing.Font("Arial", 24, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Regular)
$entityFont = New-Object System.Drawing.Font("Arial", 15, [System.Drawing.FontStyle]::Bold)
$attrFont = New-Object System.Drawing.Font("Arial", 10.5, [System.Drawing.FontStyle]::Regular)
$cardFont = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)

function CenterText {
    param($Text, $Font, $Brush, [int]$X, [int]$Y, [int]$W, [int]$H)
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

function Line {
    param([int]$X1,[int]$Y1,[int]$X2,[int]$Y2)
    $graphics.DrawLine($relPen, $X1, $Y1, $X2, $Y2)
}

function Mark {
    param([int]$X,[int]$Y,[string]$Text)
    $graphics.DrawString($Text, $cardFont, $titleBrush, $X, $Y)
}

$graphics.DrawString("TradeIQ Chen-Style ER Diagram", $titleFont, $titleBrush, 760, 20)
$graphics.DrawString("Current schema from backend/app/models.py", $subtitleFont, $mutedBrush, 860, 58)

# Entities
DrawEntity 900 120 560 120 "USERS"
DrawEntity 60 420 400 120 "PORTFOLIO_SETUP"
DrawEntity 520 420 470 150 "TRADE_LOG"
DrawEntity 1060 420 420 140 "HOLDINGS"
DrawEntity 1560 420 360 120 "RISK_METRICS"
DrawEntity 120 820 420 140 "INVESTMENT_THESIS"
DrawEntity 600 820 450 140 "THESIS_SCORES"
DrawEntity 1140 820 520 150 "WEEKLY_SCORES"
DrawEntity 830 1260 380 110 "LEADERBOARD"
DrawEntity 1280 1260 360 100 "REPORTS"

# Relationships
DrawRelationship 470 585 150 80 "HAS"
DrawRelationship 790 595 140 80 "MAKES"
DrawRelationship 1280 585 140 80 "OWNS"
DrawRelationship 1760 580 150 80 "HAS"
DrawRelationship 530 995 150 80 "WRITES"
DrawRelationship 960 1000 150 80 "SCORED_BY"
DrawRelationship 1460 1000 170 80 "GETS"
DrawRelationship 1040 1380 150 80 "RANKS"
DrawRelationship 1450 1380 150 80 "GENERATES"

# Attributes
DrawAttribute 820 55 120 44 "user_id" $true
DrawAttribute 930 55 150 44 "full_name"
DrawAttribute 1090 55 110 44 "email"
DrawAttribute 1210 55 160 44 "role"
DrawAttribute 1380 55 150 44 "password_hash"

DrawAttribute 35 360 120 42 "portfolio_id" $true
DrawAttribute 120 555 120 42 "total_capital"
DrawAttribute 250 555 110 42 "cash_balance"
DrawAttribute 365 555 130 42 "risk_appetite"
DrawAttribute 225 365 100 42 "user_id"

DrawAttribute 450 330 110 42 "trade_id" $true
DrawAttribute 420 545 120 42 "trade_date"
DrawAttribute 545 545 120 42 "stock_ticker"
DrawAttribute 675 545 120 42 "stock_name"
DrawAttribute 805 545 90 42 "sector"
DrawAttribute 500 690 150 42 "allocation_percent"
DrawAttribute 660 690 150 42 "amount_invested"
DrawAttribute 820 690 100 42 "quantity"
DrawAttribute 930 690 100 42 "buy_price"
DrawAttribute 1040 690 150 42 "current_sell_price"
DrawAttribute 1200 690 120 42 "trade_type"

DrawAttribute 1030 335 110 42 "holding_id" $true
DrawAttribute 1000 555 120 42 "stock_ticker"
DrawAttribute 1125 555 120 42 "stock_name"
DrawAttribute 1250 555 100 42 "quantity"
DrawAttribute 1360 555 130 42 "avg_buy_price"
DrawAttribute 1500 555 120 42 "current_price"
DrawAttribute 1625 555 120 42 "market_value"
DrawAttribute 1755 555 120 42 "profit_loss"

DrawAttribute 1520 330 100 42 "risk_id" $true
DrawAttribute 1490 555 130 42 "sharpe_ratio"
DrawAttribute 1630 555 90 42 "beta"
DrawAttribute 1730 555 120 42 "volatility"
DrawAttribute 1860 555 140 42 "max_drawdown"
DrawAttribute 2010 555 110 42 "var_value"

DrawAttribute 30 720 100 42 "thesis_id" $true
DrawAttribute 10 1080 120 42 "trade_id"
DrawAttribute 140 1080 130 42 "investment_style"
DrawAttribute 280 1080 100 42 "risk_level"
DrawAttribute 390 1080 150 42 "confidence_score"
DrawAttribute 170 720 140 42 "reason_text"

DrawAttribute 580 720 100 42 "score_id" $true
DrawAttribute 520 1080 130 42 "clarity_score"
DrawAttribute 655 1080 145 42 "reasoning_score"
DrawAttribute 805 1080 160 42 "risk_awareness_score"
DrawAttribute 970 1080 170 42 "market_understanding_score"
DrawAttribute 700 720 100 42 "total_score"
DrawAttribute 820 720 100 42 "feedback"

DrawAttribute 1110 720 100 42 "score_id" $true
DrawAttribute 1070 1110 120 42 "week_number"
DrawAttribute 1195 1110 140 42 "portfolio_score"
DrawAttribute 1345 1110 110 42 "risk_score"
DrawAttribute 1465 1110 115 42 "thesis_score"
DrawAttribute 1590 1110 140 42 "execution_score"
DrawAttribute 1740 1110 130 42 "strategy_score"
DrawAttribute 1880 1110 120 42 "final_score"
DrawAttribute 2010 1110 120 42 "rank_position"

DrawAttribute 830 1160 120 42 "leaderboard_id" $true
DrawAttribute 770 1460 120 42 "week_number"
DrawAttribute 900 1460 110 42 "final_score"
DrawAttribute 1015 1460 120 42 "rank_position"

DrawAttribute 1280 1160 100 42 "report_id" $true
DrawAttribute 1260 1460 120 42 "week_number"
DrawAttribute 1390 1460 120 42 "report_path"
DrawAttribute 1520 1460 120 42 "generated_at"

# Connector lines and simple cardinalities
Line 1180 240 260 420
Mark 690 285 "1"
Mark 150 410 "1"

Line 1150 240 755 420
Mark 940 295 "1"
Mark 655 410 "M"

Line 1290 240 1275 420
Mark 1280 300 "1"
Mark 1245 410 "M"

Line 1410 240 1780 420
Mark 1500 300 "1"
Mark 1730 410 "1"

Line 1100 240 330 820
Mark 720 470 "1"
Mark 190 750 "M"

Line 1210 240 810 820
Mark 1020 470 "1"
Mark 650 760 "1"

Line 1350 240 1400 820
Mark 1380 470 "1"
Mark 1385 760 "M"

Line 1200 240 980 1260
Mark 1100 520 "1"
Mark 950 1200 "M"

Line 1390 240 1460 1260
Mark 1440 520 "1"
Mark 1465 1200 "M"

Line 220 530 470 585
Line 900 585 1060 585
Line 1420 585 1560 585
Line 420 995 530 995
Line 750 1000 960 1000
Line 1630 1000 1780 1000
Line 940 1345 1040 1380
Line 1380 1345 1450 1380

$graphics.DrawString("Chen notation: rectangles = entities, ovals = attributes, diamonds = relationships.", $subtitleFont, $mutedBrush, 680, 1600)

$bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Host "Saved $outPath"
