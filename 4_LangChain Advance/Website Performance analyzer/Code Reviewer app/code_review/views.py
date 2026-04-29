import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .service import review_code_service


@csrf_exempt
def review_code_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        body = json.loads(request.body)
        code = body.get("code", "").strip()

        if not code:
            return JsonResponse({"error": "Code is required"}, status=400)

        result = review_code_service(code)

        return JsonResponse({
            "success": True,
            "review": result
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)