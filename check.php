<?php
session_start();

// إنشاء رمز التحقق العشوائي
if (!isset($_SESSION['captcha'])) {
    $_SESSION['captcha'] = rand(1000, 9999);
}

// الرابط الذي سيتم التوجيه إليه بعد التحقق الناجح
$redirect_url = "http://vip-panel.x10.bz/public/login";

// مسار ملف allowed_ips.txt
$allowed_ips_file = __DIR__ . '/App/Views/Auth/allowed_ips.txt';

// تهيئة الملف إذا لم يكن موجودًا
if (!file_exists($allowed_ips_file)) {
    file_put_contents($allowed_ips_file, "");
}

// دالة لتسجيل عنوان IP أو جملة عشوائية
function logData($data, $logFile) {
    file_put_contents($logFile, $data . "\n", FILE_APPEND);
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>التحقق من المستخدم</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .error-message {
            color: red;
            font-weight: bold;
            margin-top: 10px;
        }
        input[type="text"] {
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
    <script>
        function validateForm() {
            var userInput = document.forms["captchaForm"]["captchaInput"].value;
            var captcha = "<?php echo $_SESSION['captcha']; ?>";

            if (userInput == "") {
                alert("⚠️ الرجاء إدخال رمز التحقق.");
                return false;
            }

            if (userInput != captcha) {
                document.getElementById('error-message').innerHTML = "❌ طلبك مرفوض! رمز التحقق غير صحيح.";
                return false;
            }

            return true;
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>التحقق من المستخدم</h1>
        <p>أدخل الكود التالي: </p>
        <p style="font-size: 24px;"><?php echo $_SESSION['captcha']; ?></p>
        <form name="captchaForm" method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return validateForm()">
            <input type="text" name="captchaInput" placeholder="أدخل رمز التحقق">
            <br>
            <button type="submit">✅ تحقق</button>
        </form>

        <div id="error-message" class="error-message"></div>
    </div>

    <?php
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $userInput = $_POST['captchaInput'] ?? null;

        if ($userInput == $_SESSION['captcha']) {
            // التحقق ناجح، سجل عنوان IP وقم بتوجيه المستخدم
            logData($_SERVER['REMOTE_ADDR'], $allowed_ips_file);

            // إضافة جملة عشوائية للاختبار
            $random_string = bin2hex(random_bytes(16));
            logData("Random: " . $random_string, $allowed_ips_file);

            header("Location: $redirect_url");
            exit;
        }
    }
    ?>
</body>
</html>
