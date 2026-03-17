@RestController
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "App Running Successfully";
    }
}
