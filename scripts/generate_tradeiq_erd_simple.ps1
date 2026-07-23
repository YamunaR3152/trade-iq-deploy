Add-Type -AssemblyName System.Drawing

$outDir = Join-Path $PSScriptRoot "..\docs"
$outPath = Join-Path $outDir "tradeiq-erd-simple.png"

$width = 2000
$height = 1350

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::White)

$border = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(90, 110, 150), 3)
$line = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(95, 95, 95), 2.5)
$line.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$fill = [System.Drawing.Brushes]::White
$headFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(235, 242, 252))
$titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(26, 44, 72))
$textBrush = [System.Drawing.Brushes]::Black
$mutedBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(96, 96, 96))

$titleFont = New-Object System.Drawing.Font("Arial", 22, [System.Drawing.FontStyle]::Bold)
$smallFont = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Regular)
$smallBold = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$tinyFont = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Regular)
$cardFont = New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)

function Box {
    param([int]$X,[int]$Y,[int]$W,[int]$H,[string]$Title,[string[]]$Lines)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $graphics.FillRectangle($fill, $rect)
    $graphics.DrawRectangle($border, $rect)
    $graphics.FillRectangle($headFill, (New-Object System.Drawing.Rectangle($X, $Y, $W, 38)))
    $graphics.DrawLine($border, $X, $Y + 38, $X + $W, $Y + 38)
    $graphics.DrawString($Title, $smallBold, $titleBrush, ($X + 14), ($Y + 8))
    $yy = $Y + 48
    foreach ($l in $Lines) {
        $graphics.DrawString($l, $tinyFont, $textBrush, ($X + 14), $yy)
        $yy += 16
    }
}

function Arrow {
    param([int]$X1,[int]$Y1,[int]$X2,[int]$Y2)
    $graphics.DrawLine($line, $X1, $Y1, $X2, $Y2)
}

function Label {
    param([int]$X,[int]$Y,[string]$Text,[bool]$Cardinality = $false)
    if ($Cardinality) {
        $graphics.DrawString($Text, $cardFont, $titleBrush, $X, $Y)
    } else {
        $graphics.DrawString($Text, $tinyFont, $mutedBrush, $X, $Y)
    }
}

$graphics.DrawString("TradeIQ Database ER Diagram", $titleFont, $titleBrush, 660, 18)
$graphics.DrawString("Simplified relationship view from backend/app/models.py", $smallFont, $mutedBrush, 700, 52)

Box 760 100 480 125 "users" @(
    "PK user_id"
    "full_name, email, phone_number"
    "university, course, year_of_study"
    "participation_type, team_name, role, password_hash"
)

Box 70 325 360 130 "portfolio_setup" @(
    "PK portfolio_id"
    "FK user_id"
    "total_capital, cash_balance"
    "risk_appetite, investment_horizon, competition_round"
)

Box 520 325 450 165 "trade_log" @(
    "PK trade_id"
    "FK user_id"
    "trade_date, stock_ticker, stock_name, sector"
    "allocation_percent, amount_invested, quantity"
    "buy_price, current_sell_price, trade_type"
    "tag1, tag2, tag3, thesis"
)

Box 1070 325 410 145 "holdings" @(
    "PK holding_id"
    "FK user_id"
    "stock_ticker, stock_name"
    "quantity, avg_buy_price, current_price"
    "market_value, profit_loss"
)

Box 1560 325 360 135 "risk_metrics" @(
    "PK risk_id"
    "FK user_id"
    "sharpe_ratio, beta"
    "volatility, max_drawdown, var_value"
)

Box 260 645 430 155 "investment_thesis" @(
    "PK thesis_id"
    "FK trade_id"
    "FK user_id"
    "investment_style, risk_level, confidence_score"
    "reason_text"
)

Box 800 645 450 155 "thesis_scores" @(
    "PK score_id"
    "FK thesis_id"
    "clarity_score, reasoning_score"
    "risk_awareness_score, market_understanding_score"
    "total_score, feedback"
)

Box 1330 645 520 155 "weekly_scores" @(
    "PK score_id"
    "FK user_id"
    "week_number"
    "portfolio_score, risk_score, thesis_score"
    "execution_score, strategy_score, final_score, rank_position"
)

Box 610 980 420 120 "leaderboard" @(
    "PK leaderboard_id"
    "FK user_id"
    "week_number, final_score, rank_position"
)

Box 1120 980 360 110 "reports" @(
    "PK report_id"
    "FK user_id"
    "week_number, report_path, generated_at"
)

# relationships
Arrow 1000 225 250 325
Arrow 920 225 740 325
Arrow 1080 225 1210 325
Arrow 1080 225 1740 325

Arrow 610 490 470 645
Arrow 760 490 1010 645
Arrow 1430 490 1580 645

Arrow 820 800 790 980
Arrow 1020 800 810 980
Arrow 1070 225 850 980

Label 390 286 "1" $true
Label 250 315 "portfolio" $false
Label 835 286 "1" $true
Label 650 286 "M" $true
Label 690 315 "trades" $false
Label 1240 286 "1" $true
Label 1145 286 "M" $true
Label 1180 315 "holdings" $false
Label 1710 286 "1" $true
Label 1600 286 "1" $true
Label 1610 315 "risk profile" $false
Label 430 595 "1" $true
Label 255 595 "M" $true
Label 220 625 "thesis" $false
Label 905 595 "1" $true
Label 990 595 "1" $true
Label 905 625 "score" $false
Label 1510 595 "1" $true
Label 1600 595 "M" $true
Label 1425 625 "weekly scores" $false
Label 760 940 "scores aggregated into leaderboard" $false

$graphics.DrawString("Note: Use simple cardinality in the document: one-to-one, one-to-many, or many-to-one.", $tinyFont, $mutedBrush, 560, 1245)

$bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Host "Saved $outPath"
