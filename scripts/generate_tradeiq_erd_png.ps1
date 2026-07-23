Add-Type -AssemblyName System.Drawing

$outDir = Join-Path $PSScriptRoot "..\docs"
$outPath = Join-Path $outDir "tradeiq-erd.png"

$width = 2200
$height = 1500

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::White)

$border = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(95, 120, 160), 3)
$line = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(88, 88, 88), 2.5)
$line.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
$fill = [System.Drawing.Brushes]::White
$headFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(232, 240, 252))
$keyFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(249, 251, 255))
$titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(26, 44, 72))
$textBrush = [System.Drawing.Brushes]::Black
$mutedBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(92, 92, 92))

$titleFont = New-Object System.Drawing.Font("Arial", 24, [System.Drawing.FontStyle]::Bold)
$smallFont = New-Object System.Drawing.Font("Arial", 15, [System.Drawing.FontStyle]::Regular)
$smallBold = New-Object System.Drawing.Font("Arial", 15, [System.Drawing.FontStyle]::Bold)
$tinyFont = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Regular)
$tinyBold = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)

function Draw-Box {
    param(
        [int]$X,
        [int]$Y,
        [int]$W,
        [int]$H,
        [string]$Title,
        [string[]]$Lines,
        [bool]$Highlight = $false
    )

    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    if ($Highlight) {
        $graphics.FillRectangle($keyFill, $rect)
    } else {
        $graphics.FillRectangle($fill, $rect)
    }
    $graphics.DrawRectangle($border, $rect)
    $headerRect = New-Object System.Drawing.Rectangle($X, $Y, $W, 42)
    $graphics.FillRectangle($headFill, $headerRect)
    $graphics.DrawLine($border, $X, $Y + 42, $X + $W, $Y + 42)
    $graphics.DrawString($Title, $smallBold, $titleBrush, ($X + 14), ($Y + 10))

    $ty = $Y + 54
    foreach ($lineText in $Lines) {
        $graphics.DrawString($lineText, $tinyFont, $textBrush, ($X + 14), $ty)
        $ty += 18
    }
}

function Center-Top {
    param([int]$X,[int]$Y,[int]$W,[int]$H)
    return @{
        Left = $X
        Top = $Y
        Width = $W
        Height = $H
        CenterX = [int]($X + ($W / 2))
        CenterY = [int]($Y + ($H / 2))
    }
}

function Draw-Arrow {
    param(
        [int]$X1,
        [int]$Y1,
        [int]$X2,
        [int]$Y2
    )
    $graphics.DrawLine($line, $X1, $Y1, $X2, $Y2)
}

function Draw-Label {
    param([int]$X,[int]$Y,[string]$Text)
    $graphics.DrawString($Text, $tinyFont, $mutedBrush, $X, $Y)
}

# Title
$graphics.DrawString("TradeIQ Database ER Diagram", $titleFont, $titleBrush, 740, 20)
$graphics.DrawString("Current schema from backend/app/models.py", $smallFont, $mutedBrush, 790, 58)

# Boxes
Draw-Box 810 110 580 145 "users" @(
    "PK user_id"
    "full_name, email (unique), phone_number"
    "university, course, year_of_study"
    "participation_type, team_name, role, password_hash"
) $true

Draw-Box 80 360 450 150 "portfolio_setup" @(
    "PK portfolio_id"
    "FK user_id -> users.user_id"
    "total_capital, cash_balance"
    "risk_appetite, investment_horizon, competition_round"
)

Draw-Box 620 360 520 180 "trade_log" @(
    "PK trade_id"
    "FK user_id -> users.user_id"
    "trade_date, stock_ticker, stock_name, sector"
    "allocation_percent, amount_invested, quantity"
    "buy_price, current_sell_price, trade_type"
    "tag1, tag2, tag3, thesis"
)

Draw-Box 1200 360 450 150 "holdings" @(
    "PK holding_id"
    "FK user_id -> users.user_id"
    "stock_ticker, stock_name, quantity"
    "avg_buy_price, current_price, market_value, profit_loss"
)

Draw-Box 1700 360 420 150 "risk_metrics" @(
    "PK risk_id"
    "FK user_id -> users.user_id"
    "sharpe_ratio, beta"
    "volatility, max_drawdown, var_value"
)

Draw-Box 340 710 500 170 "investment_thesis" @(
    "PK thesis_id"
    "FK trade_id -> trade_log.trade_id"
    "FK user_id -> users.user_id"
    "investment_style, risk_level, confidence_score"
    "reason_text"
)

Draw-Box 920 710 500 170 "thesis_scores" @(
    "PK score_id"
    "FK thesis_id -> investment_thesis.thesis_id"
    "clarity_score, reasoning_score"
    "risk_awareness_score, market_understanding_score"
    "total_score, feedback"
)

Draw-Box 1500 710 560 170 "weekly_scores" @(
    "PK score_id"
    "FK user_id -> users.user_id"
    "week_number"
    "portfolio_score, risk_score, thesis_score"
    "execution_score, strategy_score"
    "final_score, rank_position"
)

Draw-Box 620 1080 500 130 "leaderboard" @(
    "PK leaderboard_id"
    "FK user_id -> users.user_id"
    "week_number, final_score, rank_position"
)

Draw-Box 1180 1080 380 120 "reports" @(
    "PK report_id"
    "FK user_id -> users.user_id"
    "week_number, report_path, generated_at"
)

# Relationships
Draw-Arrow 1090 255 305 360
Draw-Arrow 950 255 870 360
Draw-Arrow 1220 255 1425 360
Draw-Arrow 1220 255 1910 360

Draw-Arrow 850 510 590 710
Draw-Arrow 880 540 1030 710
Draw-Arrow 1520 510 1800 710

Draw-Arrow 590 880 870 1080
Draw-Arrow 1180 880 820 1080

Draw-Arrow 1090 255 1370 1080
Draw-Arrow 1090 255 1370 1080

# Labels for relationship meaning
Draw-Label 350 330 "1 user -> 0/1 portfolio"
Draw-Label 785 330 "1 user -> many trades"
Draw-Label 1320 330 "1 user -> many holdings"
Draw-Label 1830 330 "1 user -> 0/1 risk profile"
Draw-Label 445 635 "one trade -> one thesis"
Draw-Label 980 635 "one thesis -> one score"
Draw-Label 1540 635 "many users -> weekly score"
Draw-Label 760 1030 "scores aggregated per week"

$graphics.DrawString("Tip: use this diagram in the Database Design section of the technical document.", $tinyFont, $mutedBrush, 620, 1410)

$bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Host "Saved $outPath"
