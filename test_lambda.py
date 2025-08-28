
def lambda_handler(event, context):
    """
    Minimal Lambda handler to test basic functionality
    """
    # Always return a simple HTML page
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Cache-Control': 'no-cache'
        },
        'body': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lambda Test</title>
</head>
<body>
    <h1>🎉 Lambda Function is Working!</h1>
    <p>If you can see this page, the Lambda function is deployed and running correctly.</p>
    <p>Timestamp: ''' + str(context.aws_request_id if context else 'test') + '''</p>
    <script>
        console.log('Lambda function loaded successfully');
        document.body.style.fontFamily = 'Arial, sans-serif';
        document.body.style.padding = '20px';
        document.body.style.backgroundColor = '#f0f0f0';
    </script>
</body>
</html>'''
    }

