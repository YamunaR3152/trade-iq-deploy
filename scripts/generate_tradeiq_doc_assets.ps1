param(
    [string]$OutputDir
)

Add-Type -AssemblyName System.Drawing

function New-Canvas {
    param([int]$Width, [int]$Height, [System.Drawing.Color]$Background)
    $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear($Background)
    return @{ Bitmap = $bitmap; Graphics = $graphics }
}

function Save-Canvas {
    param($Canvas, [string]$Path)
    $Canvas.Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $Canvas.Graphics.Dispose()
    $Canvas.Bitmap.Dispose()
}

function Draw-RoundBox {
    param(
        $Graphics,
        [int]$X, [int]$Y, [int]$W, [int]$H,
        [System.Drawing.Color]$Fill,
        [System.Drawing.Color]$Border,
        [int]$Radius = 24
    )
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $Radius * 2
    $path.AddArc($X, $Y, $d, $d, 180, 90)
    $path.AddArc($X + $W - $d, $Y, $d, $d, 270, 90)
    $path.AddArc($X + $W - $d, $Y + $H - $d, $d, $d, 0, 90)
    $path.AddArc($X, $Y + $H - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    $brush = New-Object System.Drawing.SolidBrush $Fill
    $pen = New-Object System.Drawing.Pen $Border, 4
    $Graphics.FillPath($brush, $path)
    $Graphics.DrawPath($pen, $path)
    $brush.Dispose()
    $pen.Dispose()
    $path.Dispose()
}

function Draw-Text {
    param(
        $Graphics,
        [string]$Text,
        [string]$FontFamily = "Segoe UI",
        [float]$Size = 24,
        [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular,
        [System.Drawing.Color]$Color = [System.Drawing.Color]::Black,
        [int]$X = 0, [int]$Y = 0,
        [int]$Width = 1000
    )
    $font = New-Object System.Drawing.Font $FontFamily, $Size, $Style
    $brush = New-Object System.Drawing.SolidBrush $Color
    $rect = New-Object System.Drawing.RectangleF $X, $Y, $Width, 1000
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Near
    $format.LineAlignment = [System.Drawing.StringAlignment]::Near
    $Graphics.DrawString($Text, $font, $brush, $rect, $format)
    $font.Dispose()
    $brush.Dispose()
    $format.Dispose()
}

function Draw-CenterText {
    param(
        $Graphics,
        [string]$Text,
        [string]$FontFamily = "Segoe UI",
        [float]$Size = 24,
        [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular,
        [System.Drawing.Color]$Color = [System.Drawing.Color]::Black,
        [int]$X = 0, [int]$Y = 0,
        [int]$W = 1000, [int]$H = 200
    )
    $font = New-Object System.Drawing.Font $FontFamily, $Size, $Style
    $brush = New-Object System.Drawing.SolidBrush $Color
    $rect = New-Object System.Drawing.RectangleF $X, $Y, $W, $H
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $Graphics.DrawString($Text, $font, $brush, $rect, $format)
    $font.Dispose()
    $brush.Dispose()
    $format.Dispose()
}

function Draw-Arrow {
    param($Graphics, [int]$X1, [int]$Y1, [int]$X2, [int]$Y2, [System.Drawing.Color]$Color, [int]$Width = 5)
    $pen = New-Object System.Drawing.Pen $Color, $Width
    $pen.CustomEndCap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap 7, 7
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    $pen.Dispose()
}

function New-Card {
    param(
        $Graphics, [int]$X, [int]$Y, [int]$W, [int]$H, [string]$Title, [string]$Subtitle,
        [System.Drawing.Color]$Fill, [System.Drawing.Color]$Border, [System.Drawing.Color]$TextColor
    )
    Draw-RoundBox -Graphics $Graphics -X $X -Y $Y -W $W -H $H -Fill $Fill -Border $Border -Radius 26
    Draw-CenterText -Graphics $Graphics -Text $Title -FontFamily "Segoe UI Semibold" -Size 24 -Style Bold -Color $TextColor -X ($X + 15) -Y ($Y + 10) -W ($W - 30) -H 60
    Draw-CenterText -Graphics $Graphics -Text $Subtitle -FontFamily "Segoe UI" -Size 18 -Color $TextColor -X ($X + 20) -Y ($Y + 62) -W ($W - 40) -H ($H - 72)
}

if (-not $OutputDir) {
    throw "OutputDir is required"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# image1 - logo
$c = New-Canvas -Width 1600 -Height 700 -Background ([System.Drawing.Color]::FromArgb(10, 14, 24))
Draw-CenterText -Graphics $c.Graphics -Text "TradeIQ" -FontFamily "Segoe UI Black" -Size 72 -Style Bold -Color ([System.Drawing.Color]::White) -X 0 -Y 150 -W 1600 -H 180
Draw-CenterText -Graphics $c.Graphics -Text "SalesTrading Platform" -FontFamily "Segoe UI" -Size 24 -Color ([System.Drawing.Color]::FromArgb(120, 220, 255)) -X 0 -Y 270 -W 1600 -H 60
Save-Canvas $c (Join-Path $OutputDir 'image1.png')

# image2 - simple client/backend/db summary
$c = New-Canvas -Width 1600 -Height 900 -Background ([System.Drawing.Color]::White)
Draw-RoundBox $c.Graphics 80 80 1440 740 ([System.Drawing.Color]::FromArgb(247, 245, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) 28
Draw-CenterText $c.Graphics "SalesTrading System Summary" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(90, 61, 162)) 0 110 1600 50
New-Card $c.Graphics 140 220 400 180 "Frontend" "Expo / React Native Web on Vercel" ([System.Drawing.Color]::FromArgb(244, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 600 220 400 180 "Backend" "Flask API on Render or AWS" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
New-Card $c.Graphics 1060 220 400 180 "Database" "TiDB Cloud / MySQL-compatible" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
Draw-Arrow $c.Graphics 540 310 600 310 ([System.Drawing.Color]::FromArgb(100,100,100))
Draw-Arrow $c.Graphics 1000 310 1060 310 ([System.Drawing.Color]::FromArgb(100,100,100))
New-Card $c.Graphics 200 500 520 160 "External Data" "Yahoo Finance market data via yfinance" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 760 500 680 160 "Security and Ops" "JWT, SSL/TLS, env vars, optional Redis cache" ([System.Drawing.Color]::FromArgb(246, 250, 255)) ([System.Drawing.Color]::FromArgb(63, 105, 168)) ([System.Drawing.Color]::FromArgb(29, 57, 95))
Save-Canvas $c (Join-Path $OutputDir 'image2.png')

# image3 - architecture diagram
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "High-Level Architecture" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 60 120 360 120 "User" "Browser or mobile web" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
New-Card $c.Graphics 500 110 560 140 "Frontend" "Vercel-hosted Expo / React Native Web app" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 1130 110 400 140 "Backend API" "Flask + Gunicorn + JWT" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
Draw-Arrow $c.Graphics 420 180 500 180 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1060 180 1130 180 ([System.Drawing.Color]::FromArgb(90,90,90))
New-Card $c.Graphics 510 350 360 140 "Database" "TiDB Cloud / MySQL-compatible" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 900 350 340 140 "Cache" "Redis when enabled" ([System.Drawing.Color]::FromArgb(255, 246, 239)) ([System.Drawing.Color]::FromArgb(214, 111, 52)) ([System.Drawing.Color]::FromArgb(120, 58, 24))
New-Card $c.Graphics 1260 350 300 140 "Market Data" "Yahoo Finance via yfinance" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
Draw-Arrow $c.Graphics 780 250 690 350 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 780 250 1070 350 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1330 250 1410 350 ([System.Drawing.Color]::FromArgb(90,90,90))
Save-Canvas $c (Join-Path $OutputDir 'image3.png')

# image4 - trade execution flow
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "Trade Execution Flow" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 420 110 760 120 "1. User action" "User clicks Buy or Sell in the frontend" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 420 270 760 130 "2. Frontend request" "Frontend sends API call with JWT token" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
New-Card $c.Graphics 420 450 760 130 "3. Backend validation" "Backend checks token, cash, holdings, and price" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 420 630 760 130 "4. Database update" "Trade log, holdings, and portfolio cash are updated" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 420 810 760 120 "5. Response" "Frontend refreshes portfolio and shows the result" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
Draw-Arrow $c.Graphics 800 230 800 270 ([System.Drawing.Color]::FromArgb(70,70,70))
Draw-Arrow $c.Graphics 800 400 800 450 ([System.Drawing.Color]::FromArgb(70,70,70))
Draw-Arrow $c.Graphics 800 580 800 630 ([System.Drawing.Color]::FromArgb(70,70,70))
Draw-Arrow $c.Graphics 800 760 800 810 ([System.Drawing.Color]::FromArgb(70,70,70))
Save-Canvas $c (Join-Path $OutputDir 'image4.png')

# image5 - scoring flow
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "Scoring and Leaderboard Flow" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 540 110 520 100 "Scheduled or on-demand scoring" "Scores can be recomputed by backend logic" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
New-Card $c.Graphics 120 280 420 130 "Portfolio performance" "Profit/loss and return on capital" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 590 280 420 130 "Thesis quality" "Reasoning, clarity, and market awareness" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 1060 280 420 130 "Risk metrics" "Sharpe, beta, drawdown, and diversification" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
New-Card $c.Graphics 420 500 760 140 "Score aggregation" "Combines the score components into a final weekly score" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 420 700 760 130 "Leaderboard" "Sorted ranking view for users" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
Draw-Arrow $c.Graphics 800 210 330 280 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 210 800 280 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 210 1270 280 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 330 410 620 500 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 410 800 500 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1270 410 980 500 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 640 800 700 ([System.Drawing.Color]::FromArgb(90,90,90))
Save-Canvas $c (Join-Path $OutputDir 'image5.png')

# image6 - database model
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "Database Model" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 70 120 300 110 "users" "Account and profile data" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
New-Card $c.Graphics 430 120 300 110 "portfolio_setup" "Starting capital and settings" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 790 120 300 110 "trade_log" "Every BUY/SELL action" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 1150 120 300 110 "holdings" "Current open positions" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
New-Card $c.Graphics 250 400 340 120 "investment_thesis" "Trade reasoning text" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 640 400 340 120 "thesis_scores" "Score for the reasoning" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
New-Card $c.Graphics 1030 400 340 120 "risk_metrics" "Sharpe, beta, drawdown" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 250 680 340 120 "weekly_scores" "Weekly score snapshots" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 640 680 340 120 "leaderboard" "Ranked view of users" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
New-Card $c.Graphics 1030 680 340 120 "reports" "Generated reports" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
Draw-Arrow $c.Graphics 370 230 600 400 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 580 230 960 120 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 940 230 1040 400 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1300 230 1210 400 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 420 520 420 680 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 810 520 810 680 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1200 520 1200 680 ([System.Drawing.Color]::FromArgb(90,90,90))
Save-Canvas $c (Join-Path $OutputDir 'image6.png')

# image7 - auth flow
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "Authentication Flow" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 520 110 560 110 "1. User login/register" "User sends email and password" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 520 270 560 130 "2. Backend auth service" "Validates input, hashes password, issues JWT" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
New-Card $c.Graphics 140 470 500 140 "3. Token storage" "Web uses localStorage fallback, mobile uses in-memory token" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 960 470 500 140 "4. Protected API calls" "Authorization: Bearer <token>" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
New-Card $c.Graphics 520 700 560 120 "5. Secure access" "JWT protects all authenticated routes" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
Draw-Arrow $c.Graphics 800 220 800 270 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 400 390 470 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 800 400 1210 470 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 390 610 800 700 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1210 610 800 700 ([System.Drawing.Color]::FromArgb(90,90,90))
Save-Canvas $c (Join-Path $OutputDir 'image7.png')

# image8 - deployment view
$c = New-Canvas -Width 1600 -Height 1000 -Background ([System.Drawing.Color]::White)
Draw-CenterText $c.Graphics "Deployment View" "Segoe UI Semibold" 34 Bold ([System.Drawing.Color]::FromArgb(80, 80, 80)) 0 30 1600 60
New-Card $c.Graphics 70 140 360 120 "Vercel" "Frontend deployment and web hosting" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
New-Card $c.Graphics 460 140 360 120 "Render / AWS" "Backend API hosting" ([System.Drawing.Color]::FromArgb(239, 246, 255)) ([System.Drawing.Color]::FromArgb(70, 122, 211)) ([System.Drawing.Color]::FromArgb(32, 77, 142))
New-Card $c.Graphics 850 140 360 120 "TiDB Cloud" "MySQL-compatible managed database" ([System.Drawing.Color]::FromArgb(239, 251, 241)) ([System.Drawing.Color]::FromArgb(47, 140, 72)) ([System.Drawing.Color]::FromArgb(30, 104, 55))
New-Card $c.Graphics 1240 140 290 120 "Redis optional" "Shared cache for speed" ([System.Drawing.Color]::FromArgb(255, 250, 235)) ([System.Drawing.Color]::FromArgb(214, 146, 0)) ([System.Drawing.Color]::FromArgb(133, 78, 0))
Draw-Arrow $c.Graphics 430 200 460 200 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 820 200 850 200 ([System.Drawing.Color]::FromArgb(90,90,90))
Draw-Arrow $c.Graphics 1210 200 1240 200 ([System.Drawing.Color]::FromArgb(90,90,90))
New-Card $c.Graphics 120 420 620 170 "Production concerns" "Logging, monitoring, backups, SSL/TLS, and environment variables" ([System.Drawing.Color]::FromArgb(242, 247, 255)) ([System.Drawing.Color]::FromArgb(94, 135, 210)) ([System.Drawing.Color]::FromArgb(34, 64, 111))
New-Card $c.Graphics 820 420 680 170 "Scale-up path" "Load balancing, autoscaling, queue workers, and read replicas" ([System.Drawing.Color]::FromArgb(255, 244, 244)) ([System.Drawing.Color]::FromArgb(200, 77, 77)) ([System.Drawing.Color]::FromArgb(125, 38, 38))
New-Card $c.Graphics 400 680 800 150 "Current status" "Good for development and early production; further hardening needed for large scale" ([System.Drawing.Color]::FromArgb(245, 239, 255)) ([System.Drawing.Color]::FromArgb(120, 84, 211)) ([System.Drawing.Color]::FromArgb(61, 42, 122))
Save-Canvas $c (Join-Path $OutputDir 'image8.png')

Write-Host "Generated doc assets in $OutputDir"
